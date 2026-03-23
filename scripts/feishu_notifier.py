#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书通知集成 - 发送告警、任务完成通知、错误报告到飞书群

功能:
- 告警消息发送
- 任务完成通知
- 错误报告
- 支持 Markdown 格式
- 支持@用户

使用示例:
    from feishu_notifier import FeishuNotifier
    
    notifier = FeishuNotifier()
    
    # 发送告警
    notifier.send_alert("配置同步失败", "请检查日志")
    
    # 发送任务完成通知
    notifier.send_task_complete("TASK-001", "ClawBuilder", "实现登录功能")
    
    # 发送错误报告
    notifier.send_error_report("同步脚本", "ConnectionError", "无法连接到飞书 API")
"""

import os
import json
import hashlib
import hmac
import base64
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

try:
    import requests
except ImportError:
    print("❌ 缺少依赖：requests")
    print("请运行：pip install requests")
    exit(1)


# ==================== 配置 ====================

@dataclass
class NotificationConfig:
    """通知配置"""
    webhook_url: str
    secret: Optional[str] = None  # 可选的签名密钥
    mention_users: Optional[List[str]] = None  # 要@的用户 open_id 列表


class NotificationType(Enum):
    """通知类型"""
    ALERT = "alert"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    ERROR_REPORT = "error_report"
    INFO = "info"


# ==================== 核心类 ====================

class FeishuNotifier:
    """飞书通知器"""
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        """
        初始化飞书通知器
        
        Args:
            config: 通知配置，默认从环境变量读取
        """
        if config:
            self.config = config
        else:
            # 从环境变量读取配置
            webhook_url = os.getenv('FEISHU_WEBHOOK_URL')
            secret = os.getenv('FEISHU_WEBHOOK_SECRET')
            
            if not webhook_url:
                raise ValueError(
                    "缺少飞书 Webhook URL，请设置环境变量 FEISHU_WEBHOOK_URL\n"
                    "获取方式：飞书群 -> 设置 -> 群机器人 -> 添加机器人 -> 自定义机器人"
                )
            
            self.config = NotificationConfig(
                webhook_url=webhook_url,
                secret=secret
            )
        
        # 消息去重 (防止短时间重复发送)
        self.sent_messages: Dict[str, float] = {}
        self.dedup_window = 300  # 5 分钟去重窗口
    
    def _generate_signature(self, timestamp: str) -> str:
        """
        生成飞书 webhook 签名
        
        Args:
            timestamp: 时间戳字符串
            
        Returns:
            str: Base64 编码的签名
        """
        if not self.config.secret:
            return ""
        
        string_to_sign = f"{timestamp}\n{self.config.secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        
        return base64.b64encode(hmac_code).decode("utf-8")
    
    def _should_send(self, message_key: str) -> bool:
        """
        检查消息是否应该发送 (去重检查)
        
        Args:
            message_key: 消息唯一标识
            
        Returns:
            bool: 是否应该发送
        """
        now = time.time()
        
        # 清理过期的去重记录
        expired_keys = [
            k for k, t in self.sent_messages.items()
            if now - t > self.dedup_window
        ]
        for k in expired_keys:
            del self.sent_messages[k]
        
        # 检查是否重复
        if message_key in self.sent_messages:
            return False
        
        self.sent_messages[message_key] = now
        return True
    
    def _generate_message_key(self, content: str) -> str:
        """
        生成消息唯一标识
        
        Args:
            content: 消息内容
            
        Returns:
            str: MD5 哈希值
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _build_interactive_card(
        self,
        title: str,
        content: str,
        color: str = "red",
        mention_users: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        构建飞书交互式消息卡片
        
        Args:
            title: 卡片标题
            content: 卡片内容
            color: 颜色 (red/green/yellow/blue)
            mention_users: 要@的用户 open_id 列表
            
        Returns:
            Dict: 卡片消息 JSON
        """
        # 颜色映射
        color_map = {
            "red": "#F53F3F",
            "green": "#00B42A",
            "yellow": "#F7BA1E",
            "blue": "#3370FF"
        }
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": color
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": content
                }
            ]
        }
        
        # 添加@信息
        if mention_users:
            card["elements"].append({
                "tag": "mention_list",
                "mentions": [{"user_id": uid} for uid in mention_users]
            })
        
        return {
            "msg_type": "interactive",
            "card": json.dumps(card, ensure_ascii=False)
        }
    
    def _build_text_message(
        self,
        content: str,
        mention_users: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        构建纯文本消息
        
        Args:
            content: 消息内容
            mention_users: 要@的用户 open_id 列表
            
        Returns:
            Dict: 文本消息 JSON
        """
        if mention_users:
            # 构建@语法
            mention_str = " ".join([f"<at user_id='{uid}'></at>" for uid in mention_users])
            content = f"{mention_str}\n{content}"
        
        return {
            "msg_type": "text",
            "content": json.dumps({"text": content}, ensure_ascii=False)
        }
    
    def _send(self, message: Dict[str, Any]) -> bool:
        """
        发送消息到飞书
        
        Args:
            message: 消息字典
            
        Returns:
            bool: 是否成功
        """
        try:
            # 添加签名
            timestamp = str(int(time.time()))
            params = {}
            
            if self.config.secret:
                signature = self._generate_signature(timestamp)
                params = {
                    "timestamp": timestamp,
                    "sign": signature
                }
            
            response = requests.post(
                self.config.webhook_url,
                json=message,
                params=params,
                timeout=10
            )
            
            result = response.json()
            
            if result.get("StatusCode") == 0 or result.get("code") == 0:
                return True
            else:
                print(f"❌ 飞书消息发送失败：{result}")
                return False
                
        except Exception as e:
            print(f"❌ 发送消息异常：{e}")
            return False
    
    def send(
        self,
        title: str,
        content: str,
        msg_type: NotificationType = NotificationType.INFO,
        color: Optional[str] = None,
        mention_users: Optional[List[str]] = None,
        use_card: bool = True
    ) -> bool:
        """
        发送通知
        
        Args:
            title: 标题
            content: 内容
            msg_type: 消息类型
            color: 卡片颜色
            mention_users: 要@的用户
            use_card: 是否使用卡片消息
            
        Returns:
            bool: 是否成功
        """
        # 去重检查
        message_key = self._generate_message_key(f"{title}:{content}")
        if not self._should_send(message_key):
            print(f"⚠️ 消息去重，跳过发送")
            return False
        
        # 确定颜色
        if not color:
            color_map = {
                NotificationType.ALERT: "red",
                NotificationType.TASK_COMPLETE: "green",
                NotificationType.TASK_FAILED: "red",
                NotificationType.ERROR_REPORT: "red",
                NotificationType.INFO: "blue"
            }
            color = color_map.get(msg_type, "blue")
        
        # 确定@用户
        target_mentions = mention_users or self.config.mention_users
        
        # 构建消息
        if use_card:
            message = self._build_interactive_card(
                title=title,
                content=content,
                color=color,
                mention_users=target_mentions
            )
        else:
            full_content = f"**{title}**\n\n{content}"
            message = self._build_text_message(
                content=full_content,
                mention_users=target_mentions
            )
        
        # 发送
        success = self._send(message)
        
        if success:
            print(f"✅ 通知发送成功：{title}")
        else:
            print(f"❌ 通知发送失败：{title}")
        
        return success
    
    def send_alert(
        self,
        alert_title: str,
        alert_content: str,
        mention_users: Optional[List[str]] = None
    ) -> bool:
        """
        发送告警通知
        
        Args:
            alert_title: 告警标题
            alert_content: 告警内容
            mention_users: 要@的用户
            
        Returns:
            bool: 是否成功
        """
        content = f"🚨 **告警**\n\n{alert_content}"
        return self.send(
            title=f"🚨 {alert_title}",
            content=content,
            msg_type=NotificationType.ALERT,
            color="red",
            mention_users=mention_users
        )
    
    def send_task_complete(
        self,
        task_id: str,
        assignee: str,
        task_description: str,
        duration: Optional[str] = None
    ) -> bool:
        """
        发送任务完成通知
        
        Args:
            task_id: 任务 ID
            assignee: 负责人
            task_description: 任务描述
            duration: 耗时
            
        Returns:
            bool: 是否成功
        """
        content = f"""
✅ **任务完成**

**任务 ID**: {task_id}
**负责人**: {assignee}
**任务描述**: {task_description}
{f'**耗时**: {duration}' if duration else ''}
**完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send(
            title="✅ 任务完成通知",
            content=content.strip(),
            msg_type=NotificationType.TASK_COMPLETE,
            color="green"
        )
    
    def send_task_failed(
        self,
        task_id: str,
        assignee: str,
        task_description: str,
        error_message: str
    ) -> bool:
        """
        发送任务失败通知
        
        Args:
            task_id: 任务 ID
            assignee: 负责人
            task_description: 任务描述
            error_message: 错误信息
            
        Returns:
            bool: 是否成功
        """
        content = f"""
❌ **任务失败**

**任务 ID**: {task_id}
**负责人**: {assignee}
**任务描述**: {task_description}
**错误信息**: {error_message}
**失败时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send(
            title="❌ 任务失败通知",
            content=content.strip(),
            msg_type=NotificationType.TASK_FAILED,
            color="red"
        )
    
    def send_error_report(
        self,
        module: str,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None
    ) -> bool:
        """
        发送错误报告
        
        Args:
            module: 模块名称
            error_type: 错误类型
            error_message: 错误信息
            stack_trace: 堆栈跟踪
            
        Returns:
            bool: 是否成功
        """
        stack_trace_section = f'**堆栈跟踪**:\n```\n{stack_trace}\n```' if stack_trace else ''
        content = f"""
🐛 **错误报告**

**模块**: {module}
**错误类型**: {error_type}
**错误信息**: {error_message}
{stack_trace_section}
**报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send(
            title="🐛 错误报告",
            content=content.strip(),
            msg_type=NotificationType.ERROR_REPORT,
            color="red"
        )
    
    def send_info(
        self,
        title: str,
        content: str
    ) -> bool:
        """
        发送普通信息通知
        
        Args:
            title: 标题
            content: 内容
            
        Returns:
            bool: 是否成功
        """
        return self.send(
            title=title,
            content=content,
            msg_type=NotificationType.INFO,
            color="blue"
        )


# ==================== 便捷函数 ====================

# 全局通知器实例
_notifier: Optional[FeishuNotifier] = None


def get_notifier() -> FeishuNotifier:
    """获取全局通知器实例"""
    global _notifier
    if _notifier is None:
        try:
            _notifier = FeishuNotifier()
        except ValueError as e:
            print(f"⚠️ 通知器未配置：{e}")
            return None
    return _notifier


def send_alert(title: str, content: str) -> bool:
    """便捷函数：发送告警"""
    notifier = get_notifier()
    return notifier.send_alert(title, content) if notifier else False


def send_task_complete(task_id: str, assignee: str, description: str) -> bool:
    """便捷函数：发送任务完成通知"""
    notifier = get_notifier()
    return notifier.send_task_complete(task_id, assignee, description) if notifier else False


def send_error_report(module: str, error_type: str, message: str) -> bool:
    """便捷函数：发送错误报告"""
    notifier = get_notifier()
    return notifier.send_error_report(module, error_type, message) if notifier else False


# ==================== 命令行入口 ====================

def main():
    """命令行入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 feishu_notifier.py <command> [args]")
        print("\n可用命令:")
        print("  alert <title> <content>     发送告警")
        print("  task-complete <id> <assignee> <desc>  发送任务完成通知")
        print("  error <module> <type> <msg> 发送错误报告")
        print("  test                        发送测试消息")
        return
    
    command = sys.argv[1]
    
    try:
        notifier = FeishuNotifier()
    except ValueError as e:
        print(f"❌ 初始化失败：{e}")
        sys.exit(1)
    
    if command == 'alert':
        if len(sys.argv) < 4:
            print("用法：alert <title> <content>")
            return
        
        title = sys.argv[2]
        content = ' '.join(sys.argv[3:])
        success = notifier.send_alert(title, content)
        sys.exit(0 if success else 1)
    
    elif command == 'task-complete':
        if len(sys.argv) < 5:
            print("用法：task-complete <task_id> <assignee> <description>")
            return
        
        task_id = sys.argv[2]
        assignee = sys.argv[3]
        description = ' '.join(sys.argv[4:])
        success = notifier.send_task_complete(task_id, assignee, description)
        sys.exit(0 if success else 1)
    
    elif command == 'error':
        if len(sys.argv) < 5:
            print("用法：error <module> <error_type> <message>")
            return
        
        module = sys.argv[2]
        error_type = sys.argv[3]
        message = ' '.join(sys.argv[4:])
        success = notifier.send_error_report(module, error_type, message)
        sys.exit(0 if success else 1)
    
    elif command == 'test':
        print("发送测试消息...")
        success = notifier.send_info(
            title="🧪 测试通知",
            content=f"这是一条测试消息\n发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print(f"{'✅ 测试成功' if success else '❌ 测试失败'}")
        sys.exit(0 if success else 1)
    
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()

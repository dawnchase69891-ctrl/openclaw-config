#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 协作工具 - 带可靠性保障的 sessions_send 封装

功能:
- Agent 状态检查
- 带指数退避的重试机制
- 死信队列记录失败消息
- 异常分类处理

使用示例:
    from collaboration_utils import send_with_retry, AgentOfflineError
    
    try:
        await send_with_retry(
            target='clawbuilder',
            message='请实现用户登录功能',
            max_retries=3
        )
    except AgentOfflineError as e:
        print(f"Agent 离线：{e}")
"""

import asyncio
import random
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, asdict


# ==================== 异常定义 ====================

class CollaborationError(Exception):
    """协作异常基类"""
    pass


class AgentOfflineError(CollaborationError):
    """Agent 离线异常"""
    pass


class AgentBusyError(CollaborationError):
    """Agent 繁忙异常"""
    pass


class SessionSendError(CollaborationError):
    """sessions_send 执行异常"""
    pass


# ==================== 数据类 ====================

class AgentStatus(Enum):
    """Agent 状态枚举"""
    ONLINE = "online"
    BUSY = "busy"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


@dataclass
class DeadLetterMessage:
    """死信消息数据结构"""
    target: str
    message: str
    error_type: str
    error_message: str
    attempts: int
    failed_at: str
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


# ==================== 核心类 ====================

class CollaborationService:
    """Agent 协作服务"""
    
    def __init__(self, dead_letter_path: str = None):
        """
        初始化协作服务
        
        Args:
            dead_letter_path: 死信队列存储路径，默认 ~/.openclaw/workspace/.dead-letter/
        """
        self.dead_letter_path = Path(dead_letter_path) if dead_letter_path else \
            Path.home() / '.openclaw' / 'workspace' / '.dead-letter'
        self.dead_letter_path.mkdir(parents=True, exist_ok=True)
        
        # 重试配置
        self.max_retries = 3
        self.base_delay = 5.0  # 秒
        self.max_delay = 60.0  # 秒
        self.jitter = 0.1  # 随机抖动比例
    
    async def is_agent_online(self, agent_id: str) -> bool:
        """
        检查 Agent 是否在线
        
        Args:
            agent_id: Agent ID
            
        Returns:
            bool: 是否在线
        """
        try:
            import subprocess
            result = subprocess.run(
                ['openclaw', 'sessions', 'list', '--json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False
            
            sessions = json.loads(result.stdout)
            return any(s.get('agent_id') == agent_id for s in sessions)
            
        except Exception as e:
            print(f"检查 Agent 状态失败：{e}")
            return False
    
    async def get_agent_status(self, agent_id: str) -> AgentStatus:
        """
        获取 Agent 详细状态
        
        Args:
            agent_id: Agent ID
            
        Returns:
            AgentStatus: 状态枚举
        """
        try:
            import subprocess
            result = subprocess.run(
                ['openclaw', 'sessions', 'list', '--json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return AgentStatus.OFFLINE
            
            sessions = json.loads(result.stdout)
            for s in sessions:
                if s.get('agent_id') == agent_id:
                    if s.get('is_processing', False):
                        return AgentStatus.BUSY
                    return AgentStatus.ONLINE
            
            return AgentStatus.OFFLINE
            
        except Exception as e:
            print(f"获取 Agent 状态失败：{e}")
            return AgentStatus.UNKNOWN
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        计算重试延迟 (指数退避 + 随机抖动)
        
        Args:
            attempt: 当前尝试次数 (从 0 开始)
            
        Returns:
            float: 延迟秒数
        """
        exponential_delay = self.base_delay * (2 ** attempt)
        jitter_value = random.uniform(0, self.jitter * exponential_delay)
        return min(exponential_delay + jitter_value, self.max_delay)
    
    async def _send_message(self, target: str, message: str) -> bool:
        """
        实际发送消息 (封装 sessions_send)
        
        Args:
            target: 目标 Agent ID
            message: 消息内容
            
        Returns:
            bool: 是否成功
        """
        try:
            import subprocess
            
            result = subprocess.run(
                ['openclaw', 'sessions', 'send', '--target', target, '--message', message],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            raise SessionSendError("发送超时")
        except Exception as e:
            raise SessionSendError(f"发送失败：{e}")
    
    async def _enqueue_dead_letter(self, message: DeadLetterMessage):
        """
        将失败消息加入死信队列
        
        Args:
            message: 死信消息对象
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"dead_letter_{timestamp}_{message.target}.json"
        filepath = self.dead_letter_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(message.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"死信消息已记录：{filepath}")
    
    async def send_with_retry(
        self,
        target: str,
        message: str,
        max_retries: int = None,
        check_status: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        带重试的消息发送
        
        Args:
            target: 目标 Agent ID
            message: 消息内容
            max_retries: 最大重试次数
            check_status: 是否预先检查 Agent 状态
            metadata: 附加元数据
            
        Returns:
            bool: 是否成功
        """
        retries = max_retries or self.max_retries
        last_error = None
        
        for attempt in range(retries):
            try:
                if check_status and attempt == 0:
                    status = await self.get_agent_status(target)
                    
                    if status == AgentStatus.OFFLINE:
                        raise AgentOfflineError(f"Agent {target} 离线")
                    
                    if status == AgentStatus.BUSY:
                        raise AgentBusyError(f"Agent {target} 繁忙")
                
                success = await self._send_message(target, message)
                
                if not success:
                    raise SessionSendError("sessions_send 返回失败")
                
                print(f"✅ 消息成功发送到 {target}")
                return True
                
            except CollaborationError as e:
                last_error = e
                
                if attempt < retries - 1:
                    delay = self._calculate_delay(attempt)
                    print(f"⚠️ 第 {attempt + 1} 次尝试失败：{e}，{delay:.1f}秒后重试...")
                    await asyncio.sleep(delay)
                else:
                    print(f"❌ 所有重试失败，记录死信消息")
                    dead_letter = DeadLetterMessage(
                        target=target,
                        message=message,
                        error_type=type(e).__name__,
                        error_message=str(e),
                        attempts=retries,
                        failed_at=datetime.now().isoformat(),
                        metadata=metadata
                    )
                    await self._enqueue_dead_letter(dead_letter)
                    raise
        
        return False
    
    async def get_dead_letter_queue(self) -> List[DeadLetterMessage]:
        """获取死信队列中的所有消息"""
        messages = []
        
        for filepath in self.dead_letter_path.glob('dead_letter_*.json'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    messages.append(DeadLetterMessage(**data))
            except Exception as e:
                print(f"读取死信文件失败 {filepath}: {e}")
        
        return sorted(messages, key=lambda m: m.failed_at, reverse=True)
    
    async def retry_dead_letter(self, filepath: str) -> bool:
        """重试死信队列中的消息"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            success = await self.send_with_retry(
                target=data['target'],
                message=data['message'],
                metadata=data.get('metadata')
            )
            
            if success:
                os.remove(filepath)
                print(f"✅ 死信消息重试成功，已删除：{filepath}")
            
            return success
            
        except Exception as e:
            print(f"❌ 死信消息重试失败：{e}")
            return False


# ==================== 便捷函数 ====================

_collaboration_service: Optional[CollaborationService] = None


def get_collaboration_service() -> CollaborationService:
    """获取全局协作服务实例"""
    global _collaboration_service
    if _collaboration_service is None:
        _collaboration_service = CollaborationService()
    return _collaboration_service


async def send_with_retry(
    target: str,
    message: str,
    max_retries: int = 3,
    check_status: bool = True
) -> bool:
    """便捷函数：带重试的消息发送"""
    service = get_collaboration_service()
    return await service.send_with_retry(target, message, max_retries, check_status)


async def check_agent_status(agent_id: str) -> AgentStatus:
    """便捷函数：检查 Agent 状态"""
    service = get_collaboration_service()
    return await service.get_agent_status(agent_id)


async def get_dead_letters() -> List[DeadLetterMessage]:
    """便捷函数：获取死信队列"""
    service = get_collaboration_service()
    return await service.get_dead_letter_queue()


# ==================== 命令行入口 ====================

async def main():
    """命令行测试入口"""
    import sys
    
    service = CollaborationService()
    
    if len(sys.argv) < 2:
        print("用法：python3 collaboration_utils.py <command> [args]")
        print("\n可用命令:")
        print("  check <agent_id>           检查 Agent 状态")
        print("  send <agent_id> <message>  发送消息 (带重试)")
        print("  list-dead-letters          列出死信队列")
        print("  retry <filepath>           重试死信消息")
        return
    
    command = sys.argv[1]
    
    if command == 'check':
        if len(sys.argv) < 3:
            print("用法：check <agent_id>")
            return
        
        agent_id = sys.argv[2]
        status = await service.get_agent_status(agent_id)
        print(f"Agent {agent_id} 状态：{status.value}")
    
    elif command == 'send':
        if len(sys.argv) < 4:
            print("用法：send <agent_id> <message>")
            return
        
        agent_id = sys.argv[2]
        message = ' '.join(sys.argv[3:])
        
        try:
            success = await service.send_with_retry(agent_id, message)
            if success:
                print("✅ 发送成功")
            else:
                print("❌ 发送失败")
        except CollaborationError as e:
            print(f"❌ 发送失败：{e}")
    
    elif command == 'list-dead-letters':
        messages = await service.get_dead_letter_queue()
        
        if not messages:
            print("死信队列为空")
            return
        
        print(f"死信队列 ({len(messages)} 条):")
        for msg in messages[:10]:
            print(f"  - {msg.failed_at}: {msg.target} - {msg.error_type}")
    
    elif command == 'retry':
        if len(sys.argv) < 3:
            print("用法：retry <filepath>")
            return
        
        filepath = sys.argv[2]
        success = await service.retry_dead_letter(filepath)
        if success:
            print("✅ 重试成功")
        else:
            print("❌ 重试失败")
    
    else:
        print(f"❌ 未知命令：{command}")


if __name__ == '__main__':
    asyncio.run(main())

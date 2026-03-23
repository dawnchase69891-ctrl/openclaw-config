#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClawCoordinator·任务检查脚本

功能：
- 每 4 小时检查飞书多维表格任务状态
- 识别逾期、阻塞、即将到期的任务
- 发送进度提醒给相关负责人

执行时间：00:00, 04:00, 08:00, 12:00, 16:00, 20:00
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'

# 飞书多维表格配置
BITABLE_APP_TOKEN = "Gl4ibvzo7aJ8Uxsi3qbcHlSgnzb"
BITABLE_TABLE_ID = "tbllY5zE0YqSqtyJ"

# 飞书应用配置 (使用用户 OAuth)
FEISHU_APP_ID = "cli_a917e43cb0e29bc2"
FEISHU_APP_SECRET = "GfPZSnzF5cjlJsGcugIhSfHHi3HvAEHM"

# 群聊配置
TASK_NOTIFY_GROUP_ID = "oc_88d2f2fdba3985ce4af408c6084faff1"  # 任务通知群
CEO_OPEN_ID = "ou_9c111f465a69f41b26e059801d9b79f0"  # 骐骥


def get_tenant_access_token() -> str:
    """获取飞书应用访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    resp = requests.post(url, json=payload, timeout=10)
    result = resp.json()
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    else:
        raise Exception(f"获取令牌失败：{result}")


def get_bitable_records(token: str) -> List[Dict]:
    """获取多维表格所有任务记录"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{BITABLE_TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    all_records = []
    page_token = None
    
    while True:
        params = {"page_size": 500}
        if page_token:
            params["page_token"] = page_token
        
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        result = resp.json()
        
        if result.get("code") != 0:
            print(f"❌ 获取任务列表失败：{result}")
            break
        
        records = result.get("data", {}).get("items", [])
        all_records.extend(records)
        
        page_token = result.get("data", {}).get("page_token")
        if not page_token:
            break
    
    return all_records


def parse_task_record(record: Dict) -> Dict:
    """解析任务记录字段"""
    fields = record.get("fields", {})
    
    # 提取关键字段
    task_id = record.get("record_id", "")
    title = fields.get("任务标题", "无标题")
    description = fields.get("任务描述", "")
    status = fields.get("状态", "待开始")
    priority = fields.get("优先级", "P2")
    role = fields.get("执行角色", "")
    owner = fields.get("负责人", "")
    
    # 解析时间字段 (飞书日期是毫秒时间戳)
    due_date = None
    due_date_str = fields.get("截止时间")
    if due_date_str and isinstance(due_date_str, (int, float)):
        due_date = datetime.fromtimestamp(due_date_str / 1000)
    
    completed_date = None
    completed_date_str = fields.get("完成时间")
    if completed_date_str and isinstance(completed_date_str, (int, float)):
        completed_date = datetime.fromtimestamp(completed_date_str / 1000)
    
    block_reason = fields.get("阻塞原因", "")
    
    return {
        "task_id": task_id,
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "role": role,
        "owner": owner,
        "due_date": due_date,
        "completed_date": completed_date,
        "block_reason": block_reason,
    }


def check_task_status(tasks: List[Dict]) -> Dict:
    """
    检查任务状态
    
    返回：
    - overdue_tasks: 逾期任务列表
    - blocking_tasks: 阻塞任务列表
    - due_soon_tasks: 即将到期任务 (24 小时内)
    - in_progress_tasks: 进行中的任务
    """
    now = datetime.now()
    today_end = now.replace(hour=23, minute=59, second=59)
    tomorrow_end = now + timedelta(days=1)
    
    overdue_tasks = []
    blocking_tasks = []
    due_soon_tasks = []
    in_progress_tasks = []
    
    for task in tasks:
        status = task["status"]
        due_date = task["due_date"]
        block_reason = task["block_reason"]
        
        # 跳过已完成任务
        if status == "已完成":
            continue
        
        # 检查阻塞任务
        if block_reason and block_reason.strip():
            blocking_tasks.append(task)
        
        # 检查逾期任务
        if due_date and due_date < now:
            overdue_tasks.append(task)
        # 检查即将到期任务 (24 小时内)
        elif due_date and due_date < tomorrow_end:
            due_soon_tasks.append(task)
        
        # 收集中进行任务
        if status == "进行中":
            in_progress_tasks.append(task)
    
    return {
        "overdue_tasks": overdue_tasks,
        "blocking_tasks": blocking_tasks,
        "due_soon_tasks": due_soon_tasks,
        "in_progress_tasks": in_progress_tasks,
        "check_time": now.strftime("%Y-%m-%d %H:%M:%S"),
    }


def format_task_message(task: Dict) -> str:
    """格式化单条任务消息"""
    msg = f"📋 **{task['title']}**\n"
    msg += f"   状态：{task['status']} | 优先级：{task['priority']} | 角色：{task['role']}\n"
    if task['owner']:
        msg += f"   负责人：{task['owner']}\n"
    if task['due_date']:
        due_str = task['due_date'].strftime("%m-%d %H:%M")
        msg += f"   截止时间：{due_str}\n"
    if task['block_reason']:
        msg += f"   ⚠️ 阻塞：{task['block_reason']}\n"
    return msg


def send_feishu_message(token: str, chat_id: str, content: str, msg_type: str = "text", receive_id_type: str = "chat_id"):
    """发送飞书消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 构建消息内容
    if msg_type == "text":
        msg_content = json.dumps({"text": content})
    elif msg_type == "post":
        msg_content = json.dumps({
            "zh_cn": {
                "title": "任务检查报告",
                "content": [[{"tag": "text", "text": content}]]
            }
        })
    
    payload = {
        "receive_id": chat_id,
        "msg_type": msg_type,
        "content": msg_content
    }
    
    params = {"receive_id_type": receive_id_type}
    resp = requests.post(url, headers=headers, json=payload, params=params, timeout=10)
    result = resp.json()
    
    if result.get("code") == 0:
        print(f"✅ 消息已发送到群：{chat_id}")
        return True
    else:
        print(f"❌ 发送消息失败：{result}")
        return False


def generate_check_report(status: Dict) -> str:
    """生成检查报告"""
    report = f"🔍 **任务检查报告**\n"
    report += f"检查时间：{status['check_time']}\n\n"
    
    # 逾期任务
    if status['overdue_tasks']:
        report += f"🚨 **逾期任务 ({len(status['overdue_tasks'])}个)**\n"
        for task in status['overdue_tasks']:
            report += format_task_message(task) + "\n"
    else:
        report += "✅ 无逾期任务\n"
    
    report += "\n"
    
    # 阻塞任务
    if status['blocking_tasks']:
        report += f"⚠️ **阻塞任务 ({len(status['blocking_tasks'])}个)**\n"
        for task in status['blocking_tasks']:
            report += format_task_message(task) + "\n"
    else:
        report += "✅ 无阻塞任务\n"
    
    report += "\n"
    
    # 即将到期任务
    if status['due_soon_tasks']:
        report += f"⏰ **即将到期任务 ({len(status['due_soon_tasks'])}个)**\n"
        for task in status['due_soon_tasks']:
            report += format_task_message(task) + "\n"
    else:
        report += "✅ 无即将到期任务\n"
    
    report += "\n"
    
    # 进行中任务统计
    report += f"📊 **进行中任务**: {len(status['in_progress_tasks'])}个\n"
    
    return report


def main():
    """主函数"""
    print("=" * 60)
    print("🐎 ClawCoordinator·任务检查")
    print(f"📅 执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 1. 获取访问令牌
        print("\n🔑 获取飞书访问令牌...")
        token = get_tenant_access_token()
        print("✅ 令牌获取成功")
        
        # 2. 获取任务列表
        print("\n📋 获取任务列表...")
        records = get_bitable_records(token)
        print(f"✅ 共获取 {len(records)} 条任务记录")
        
        # 3. 解析任务
        print("\n🔍 解析任务状态...")
        tasks = [parse_task_record(r) for r in records]
        
        # 4. 检查任务状态
        print("\n📊 检查任务状态...")
        status = check_task_status(tasks)
        
        print(f"   - 逾期任务：{len(status['overdue_tasks'])}个")
        print(f"   - 阻塞任务：{len(status['blocking_tasks'])}个")
        print(f"   - 即将到期：{len(status['due_soon_tasks'])}个")
        print(f"   - 进行中：{len(status['in_progress_tasks'])}个")
        
        # 5. 生成报告
        print("\n📝 生成检查报告...")
        report = generate_check_report(status)
        
        # 6. 发送通知
        print("\n📬 发送通知到群聊...")
        if status['overdue_tasks'] or status['blocking_tasks'] or status['due_soon_tasks']:
            # 有问题时发送详细报告
            send_feishu_message(token, TASK_NOTIFY_GROUP_ID, report, msg_type="text")
        else:
            # 无问题时发送简要报告
            brief_report = f"✅ 任务检查完成\n时间：{status['check_time']}\n状态：一切正常，无逾期/阻塞/即将到期任务"
            send_feishu_message(token, TASK_NOTIFY_GROUP_ID, brief_report, msg_type="text")
        
        # 7. 保存检查日志
        log_file = WORKSPACE / 'logs' / 'task_check' / f"{datetime.now().strftime('%Y-%m-%d')}_check.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"检查时间：{status['check_time']}\n")
            f.write(f"逾期：{len(status['overdue_tasks'])} | 阻塞：{len(status['blocking_tasks'])} | 即将到期：{len(status['due_soon_tasks'])}\n")
        
        print("\n" + "=" * 60)
        print("✅ 任务检查完成")
        print("=" * 60)
        
        return {
            "success": True,
            "check_time": status['check_time'],
            "overdue_count": len(status['overdue_tasks']),
            "blocking_count": len(status['blocking_tasks']),
            "due_soon_count": len(status['due_soon_tasks']),
            "in_progress_count": len(status['in_progress_tasks']),
        }
        
    except Exception as e:
        print(f"\n❌ 执行失败：{e}")
        import traceback
        traceback.print_exc()
        
        # 发送错误通知
        try:
            token = get_tenant_access_token()
            error_msg = f"❌ 任务检查失败\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n错误：{str(e)}"
            send_feishu_message(token, TASK_NOTIFY_GROUP_ID, error_msg, msg_type="text")
        except:
            pass
        
        return {
            "success": False,
            "error": str(e),
        }


if __name__ == '__main__':
    result = main()
    print(f"\n执行结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 根据执行结果返回退出码
    sys.exit(0 if result['success'] else 1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClawCoordinator·任务汇报脚本

功能：
- 每天 21:00 汇总当日任务完成情况
- 生成任务日报
- 发送给骐骥 (CEO)

执行时间：每天 21:00
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

# 飞书应用配置
FEISHU_APP_ID = "cli_a917e43cb0e29bc2"
FEISHU_APP_SECRET = "GfPZSnzF5cjlJsGcugIhSfHHi3HvAEHM"

# 通知配置
CEO_OPEN_ID = "ou_9c111f465a69f41b26e059801d9b79f0"  # 骐骥
TASK_NOTIFY_GROUP_ID = "oc_88d2f2fdba3985ce4af408c6084faff1"  # 任务通知群


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
    
    task_id = record.get("record_id", "")
    title = fields.get("任务标题", "无标题")
    description = fields.get("任务描述", "")
    status = fields.get("状态", "待开始")
    priority = fields.get("优先级", "P2")
    task_type = fields.get("任务类型", "")
    role = fields.get("执行角色", "")
    owner = fields.get("负责人", "")
    
    # 解析时间字段
    created_time = None
    created_time_str = fields.get("创建时间")
    if created_time_str and isinstance(created_time_str, (int, float)):
        created_time = datetime.fromtimestamp(created_time_str / 1000)
    
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
        "task_type": task_type,
        "role": role,
        "owner": owner,
        "created_time": created_time,
        "due_date": due_date,
        "completed_date": completed_date,
        "block_reason": block_reason,
    }


def filter_today_tasks(tasks: List[Dict], target_date: datetime) -> Dict:
    """
    筛选今日任务
    
    返回：
    - completed_today: 今日完成的任务
    - new_today: 今日创建的任务
    - overdue: 逾期任务
    - in_progress: 进行中的任务
    """
    today_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    completed_today = []
    new_today = []
    overdue = []
    in_progress = []
    
    for task in tasks:
        status = task["status"]
        completed_date = task["completed_date"]
        created_time = task["created_time"]
        due_date = task["due_date"]
        
        # 今日完成的任务
        if completed_date and today_start <= completed_date <= today_end:
            completed_today.append(task)
        
        # 今日创建的任务
        if created_time and today_start <= created_time <= today_end:
            new_today.append(task)
        
        # 逾期任务 (未完成且已过期)
        if status != "已完成" and due_date and due_date < today_start:
            overdue.append(task)
        
        # 进行中的任务
        if status == "进行中":
            in_progress.append(task)
    
    return {
        "completed_today": completed_today,
        "new_today": new_today,
        "overdue": overdue,
        "in_progress": in_progress,
    }


def format_task_brief(task: Dict) -> str:
    """格式化任务简报"""
    msg = f"• {task['title']}"
    if task['role']:
        msg += f" [{task['role']}]"
    if task['owner']:
        msg += f" @ {task['owner']}"
    if task['priority'] == "P1":
        msg += " 🔴"
    elif task['priority'] == "P2":
        msg += " 🟡"
    return msg


def generate_daily_report(today_stats: Dict, report_date: datetime) -> str:
    """生成任务日报"""
    date_str = report_date.strftime("%Y-%m-%d (%A)")
    
    report = f"📊 **任务日报** | {date_str}\n\n"
    
    # 今日完成情况
    report += f"✅ **今日完成 ({len(today_stats['completed_today'])}个)**\n"
    if today_stats['completed_today']:
        for task in today_stats['completed_today']:
            report += format_task_brief(task) + "\n"
    else:
        report += "   无完成任务\n"
    
    report += "\n"
    
    # 新增任务
    report += f"🆕 **新增任务 ({len(today_stats['new_today'])}个)**\n"
    if today_stats['new_today']:
        for task in today_stats['new_today']:
            report += format_task_brief(task) + "\n"
    else:
        report += "   无新增任务\n"
    
    report += "\n"
    
    # 逾期任务
    report += f"🚨 **逾期任务 ({len(today_stats['overdue'])}个)**\n"
    if today_stats['overdue']:
        for task in today_stats['overdue']:
            report += format_task_brief(task) + "\n"
            if task['block_reason']:
                report += f"   ⚠️ 阻塞：{task['block_reason']}\n"
    else:
        report += "   无逾期任务\n"
    
    report += "\n"
    
    # 进行中任务
    report += f"🔄 **进行中 ({len(today_stats['in_progress'])}个)**\n"
    if today_stats['in_progress']:
        for task in today_stats['in_progress'][:10]:  # 限制显示 10 个
            report += format_task_brief(task) + "\n"
        if len(today_stats['in_progress']) > 10:
            report += f"   ... 还有 {len(today_stats['in_progress']) - 10} 个任务\n"
    else:
        report += "   无进行中任务\n"
    
    report += "\n"
    
    # 统计汇总
    total_completed = len(today_stats['completed_today'])
    total_new = len(today_stats['new_today'])
    total_overdue = len(today_stats['overdue'])
    total_in_progress = len(today_stats['in_progress'])
    
    report += f"📈 **今日汇总**\n"
    report += f"   完成：{total_completed} | 新增：{total_new} | 逾期：{total_overdue} | 进行中：{total_in_progress}\n"
    
    # 完成率计算
    if total_new + total_completed > 0:
        completion_rate = total_completed / (total_new + total_completed) * 100
        report += f"   完成率：{completion_rate:.1f}%\n"
    
    return report


def send_feishu_message(token: str, receive_id: str, content: str, msg_type: str = "text", receive_id_type: str = "open_id"):
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
                "title": "任务日报",
                "content": [[{"tag": "text", "text": content}]]
            }
        })
    
    payload = {
        "receive_id": receive_id,
        "msg_type": msg_type,
        "content": msg_content
    }
    
    # 如果是 open_id，需要指定 receive_id_type
    if receive_id_type == "open_id":
        params = {"receive_id_type": "open_id"}
        resp = requests.post(url, headers=headers, json=payload, params=params, timeout=10)
    else:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
    
    result = resp.json()
    
    if result.get("code") == 0:
        print(f"✅ 消息已发送：{receive_id}")
        return True
    else:
        print(f"❌ 发送消息失败：{result}")
        return False


def create_feishu_doc(token: str, title: str, content: str, folder_token: str = "") -> Optional[str]:
    """创建飞书云文档"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 创建文档
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    payload = {
        "title": title,
        "folder_token": folder_token
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    result = resp.json()
    
    if result.get("code") == 0:
        doc_id = result.get("data", {}).get("document_id")
        doc_url = f"https://bytedance.larkoffice.com/docx/{doc_id}"
        return doc_url
    else:
        print(f"❌ 创建文档失败：{result}")
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("🐎 ClawCoordinator·任务汇报")
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
        print("\n🔍 解析任务...")
        tasks = [parse_task_record(r) for r in records]
        
        # 4. 筛选今日任务
        print("\n📊 筛选今日任务...")
        today = datetime.now()
        today_stats = filter_today_tasks(tasks, today)
        
        print(f"   - 今日完成：{len(today_stats['completed_today'])}个")
        print(f"   - 今日新增：{len(today_stats['new_today'])}个")
        print(f"   - 逾期任务：{len(today_stats['overdue'])}个")
        print(f"   - 进行中：{len(today_stats['in_progress'])}个")
        
        # 5. 生成日报
        print("\n📝 生成任务日报...")
        report = generate_daily_report(today_stats, today)
        
        # 6. 发送给骐骥
        print("\n📬 发送日报给骐骥...")
        send_feishu_message(token, CEO_OPEN_ID, report, msg_type="text", receive_id_type="open_id")
        
        # 7. 发送到任务群
        print("\n📬 发送日报到任务群...")
        send_feishu_message(token, TASK_NOTIFY_GROUP_ID, report, msg_type="text")
        
        # 8. 创建飞书文档存档
        print("\n📄 创建飞书文档存档...")
        doc_title = f"🐎 任务日报 {today.strftime('%Y-%m-%d')}"
        # 使用公司事务/日报/文件夹 Token
        folder_token = "HV72frYGNlm3sVdE1vIcYSCHnac"
        doc_url = create_feishu_doc(token, doc_title, report, folder_token)
        if doc_url:
            print(f"✅ 文档已创建：{doc_url}")
        else:
            print("⚠️ 文档创建失败")
        
        # 9. 保存日志
        log_file = WORKSPACE / 'logs' / 'task_report' / f"{today.strftime('%Y-%m-%d')}_report.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"汇报时间：{today.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"文档链接：{doc_url or 'N/A'}\n\n")
            f.write(report)
        
        print("\n" + "=" * 60)
        print("✅ 任务汇报完成")
        print("=" * 60)
        
        return {
            "success": True,
            "report_time": today.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_count": len(today_stats['completed_today']),
            "new_count": len(today_stats['new_today']),
            "overdue_count": len(today_stats['overdue']),
            "in_progress_count": len(today_stats['in_progress']),
            "doc_url": doc_url,
        }
        
    except Exception as e:
        print(f"\n❌ 执行失败：{e}")
        import traceback
        traceback.print_exc()
        
        # 发送错误通知
        try:
            token = get_tenant_access_token()
            error_msg = f"❌ 任务汇报失败\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n错误：{str(e)}"
            send_feishu_message(token, CEO_OPEN_ID, error_msg, msg_type="text", receive_id_type="open_id")
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

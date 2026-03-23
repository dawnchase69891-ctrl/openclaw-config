#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赤兔计划 - 任务扫描与派发脚本
执行时间：每4小时
功能：
1. 扫描延期任务并升级
2. 扫描新任务并派发给对应角色
3. 发送汇总报告
"""

import json
from datetime import datetime

# 角色映射
ROLE_MAP = {
    "开发": "ClawBuilder",
    "设计": "ClawDesigner",
    "运营": "ClawOps",
    "分析": "ClawHunter",
    "市场": "ClawMarketer",
}

def scan_overdue_tasks(records):
    """扫描延期任务"""
    now_ts = int(datetime.now().timestamp() * 1000)
    overdue = []
    
    for record in records:
        fields = record.get('fields', {})
        due_ts = fields.get('计划结束时间', 0)
        status = fields.get('状态', '')
        
        if due_ts < now_ts and status != '已完成':
            days_overdue = (now_ts - due_ts) // 86400000
            overdue.append({
                'record': record,
                'days_overdue': days_overdue
            })
    
    return overdue

def scan_new_tasks(records):
    """扫描新任务（状态=待开始）"""
    new_tasks = []
    
    for record in records:
        fields = record.get('fields', {})
        status = fields.get('状态', '')
        
        if status == '待开始':
            new_tasks.append(record)
    
    return new_tasks

def assign_task(record):
    """派发任务给负责人"""
    fields = record.get('fields', {})
    task_name = fields.get('任务名称', '')
    role = fields.get('负责角色', '')
    
    message = f"""
## 🔔 新任务派发

**任务**：{task_name}
**负责角色**：{role}
**截止时间**：{fields.get('计划结束时间', '待定')}

请及时查看任务详情并开始执行。
"""
    print(f"[派发] 任务: {task_name} → 角色: {role}")
    return message

def escalate_overdue(record, days_overdue):
    """延期任务升级"""
    fields = record.get('fields', {})
    task_name = fields.get('任务名称', '')
    
    if days_overdue >= 7:
        level = "L4-严重"
    elif days_overdue >= 4:
        level = "L3-警告"
    elif days_overdue >= 2:
        level = "L2-关注"
    else:
        level = "L1-观察"
    
    print(f"[延期{level}] 任务: {task_name}, 延期{days_overdue}天")
    return level

def main():
    print(f"\n{'='*50}")
    print(f"[{datetime.now()}] 任务扫描开始")
    print(f"{'='*50}")
    
    app_token = "UdRjbT10baQ5zAsa6zpcrsAbnIQ"
    table_id = "tblcwPfdF6e6DLAy"
    
    # TODO: 实际调用飞书API获取任务列表
    records = []
    
    # 1. 扫描延期任务
    print("\n📅 延期任务扫描:")
    overdue_tasks = scan_overdue_tasks(records)
    if overdue_tasks:
        for item in overdue_tasks:
            escalate_overdue(item['record'], item['days_overdue'])
    else:
        print("  ✅ 无延期任务")
    
    # 2. 扫描新任务并派发
    print("\n🚀 新任务派发:")
    new_tasks = scan_new_tasks(records)
    if new_tasks:
        for task in new_tasks:
            assign_task(task)
    else:
        print("  ✅ 无待派发任务")
    
    # 3. 统计
    print("\n📊 任务统计:")
    print(f"  延期任务: {len(overdue_tasks)} 个")
    print(f"  待派发任务: {len(new_tasks)} 个")
    
    print(f"\n[{datetime.now()}] 任务扫描完成")

if __name__ == "__main__":
    main()
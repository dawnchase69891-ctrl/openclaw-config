#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
骐骥工作日历自动同步脚本

功能：
1. 创建每日工作日报事件
2. 更新任务状态到日历
3. 发送总结邮件
"""

import subprocess
import json
from datetime import datetime, timedelta
import sys

# 配置
USER_EMAIL = "dawnchase69891@gmail.com"

def run_gog_command(args):
    """运行 gog 命令"""
    cmd = ["gog"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def create_daily_event(date, tasks_done, tasks_in_progress, tasks_planned):
    """创建每日工作事件"""
    summary = f"🐎 骐骥工作日报 - {date}"
    
    description = "【今日完成】\n"
    for task in tasks_done:
        description += f"✅ {task}\n"
    
    description += "\n【进行中】\n"
    for task in tasks_in_progress:
        description += f"🔄 {task}\n"
    
    description += "\n【计划】\n"
    for task in tasks_planned:
        description += f"📋 {task}\n"
    
    # 创建事件（每天 17:00）
    from_time = f"{date}T17:00:00+08:00"
    to_time = f"{date}T18:00:00+08:00"
    
    returncode, stdout, stderr = run_gog_command([
        "calendar", "create", "primary",
        "--summary", summary,
        "--from", from_time,
        "--to", to_time,
        "--description", description
    ])
    
    if returncode == 0:
        print(f"✅ 日历事件创建成功：{summary}")
        return True
    else:
        print(f"❌ 日历事件创建失败：{stderr}")
        return False

def upload_report_to_drive(report_path):
    """上传报告到 Drive"""
    returncode, stdout, stderr = run_gog_command([
        "drive", "upload", report_path
    ])
    
    if returncode == 0:
        print(f"✅ 报告上传成功：{stdout.split()[0]}")
        return True
    else:
        print(f"❌ 报告上传失败：{stderr}")
        return False

def send_summary_email(subject, body):
    """发送总结邮件"""
    returncode, stdout, stderr = run_gog_command([
        "gmail", "send",
        "--to", USER_EMAIL,
        "--subject", subject,
        "--body", body
    ])
    
    if returncode == 0:
        print(f"✅ 邮件发送成功")
        return True
    else:
        print(f"❌ 邮件发送失败：{stderr}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🐎 骐骥工作日历同步")
    print("=" * 60)
    
    # 示例数据（实际使用时从任务系统读取）
    date = datetime.now().strftime("%Y-%m-%d")
    
    tasks_done = [
        "飞书机器人配置",
        "Google Workspace 配置",
        "收盘报告生成",
        "每日验证完成"
    ]
    
    tasks_in_progress = [
        "iPhone 语音交互配置",
        "项目管理工具选型"
    ]
    
    tasks_planned = [
        "TTS 语音回复功能",
        "工作日历自动同步"
    ]
    
    # 创建日历事件
    print("\n📅 创建日历事件...")
    create_daily_event(date, tasks_done, tasks_in_progress, tasks_planned)
    
    # 上传报告
    print("\n📁 上传报告到 Drive...")
    report_path = f"/home/uos/.openclaw/workspace/reports/stock_daily_report_{date.replace('-', '')}.pdf"
    upload_report_to_drive(report_path)
    
    print("\n" + "=" * 60)
    print("✅ 同步完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()

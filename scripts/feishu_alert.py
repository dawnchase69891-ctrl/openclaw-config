#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书警报推送
将智能警报发送到飞书

开市时间报警规则:
- 交易日：周一至周五
- 时段：09:30-11:30 (上午), 13:00-15:00 (下午)
- 闭市时间不报警
"""

import sqlite3
import requests
import json
from datetime import datetime
import os

DB_PATH = os.path.expanduser('~/.openclaw/workspace/stock_database.db')

def is_market_hours():
    """判断是否在开市时间"""
    now = datetime.now()
    
    # 周末不报警
    if now.weekday() >= 5:  # 5=周六，6=周日
        return False
    
    # 检查是否在开市时段
    current_time = now.hour * 100 + now.minute
    
    # 上午：09:30-11:30
    morning_start = 930  # 09:30
    morning_end = 1130   # 11:30
    
    # 下午：13:00-15:00
    afternoon_start = 1300  # 13:00
    afternoon_end = 1500    # 15:00
    
    if morning_start <= current_time <= morning_end:
        return True
    if afternoon_start <= current_time <= afternoon_end:
        return True
    
    return False

# 飞书 Webhook (已配置)
FEISHU_WEBHOOK = 'https://open.feishu.cn/open-apis/bot/v2/hook/475f79a4-dffc-4e4f-82e8-d483581b86ca'

def get_unsent_alerts():
    """获取未发送的警报"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, alert_type, stock_code, stock_name, alert_level,
               message, current_price, trigger_value, created_at
        FROM alert_history
        WHERE is_sent = 0
        ORDER BY created_at DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    alerts = []
    for row in rows:
        alerts.append({
            'id': row[0],
            'alert_type': row[1],
            'stock_code': row[2],
            'stock_name': row[3],
            'alert_level': row[4],
            'message': row[5],
            'current_price': row[6],
            'trigger_value': row[7],
            'created_at': row[8],
        })
    
    return alerts

def format_alert_message(alerts):
    """格式化警报消息"""
    if not alerts:
        return None
    
    # 按级别排序
    high_alerts = [a for a in alerts if a['alert_level'] == 'high']
    medium_alerts = [a for a in alerts if a['alert_level'] == 'medium']
    
    lines = []
    
    if high_alerts:
        lines.append("🔴 **高危警报**")
        for alert in high_alerts:
            lines.append(f"  • {alert['message']}")
            lines.append(f"    现价：¥{alert['current_price']:.2f} | 触发值：{alert['trigger_value']}")
    
    if medium_alerts:
        if high_alerts:
            lines.append("")
        lines.append("🟡 **注意警报**")
        for alert in medium_alerts:
            lines.append(f"  • {alert['message']}")
            lines.append(f"    现价：¥{alert['current_price']:.2f} | 触发值：{alert['trigger_value']}")
    
    lines.append("")
    lines.append(f"_生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}_")
    
    return "\n".join(lines)

def send_feishu_alert(message):
    """发送飞书警报"""
    if not FEISHU_WEBHOOK:
        print("⚠️  未配置飞书 Webhook，跳过发送")
        print("\n📱 警报内容:")
        print(message)
        return False
    
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    try:
        resp = requests.post(FEISHU_WEBHOOK, json=payload, timeout=10)
        if resp.status_code == 200:
            print("✅ 飞书警报已发送")
            return True
        else:
            print(f"❌ 发送失败：{resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ 发送异常：{e}")
        return False

def mark_alerts_sent(alerts):
    """标记警报为已发送"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for alert in alerts:
        cursor.execute('''
            UPDATE alert_history
            SET is_sent = 1, sent_at = ?
            WHERE id = ?
        ''', (now, alert['id']))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("=" * 80)
    print("📱 飞书警报推送")
    print("=" * 80)
    
    # 检查是否在开市时间
    if not is_market_hours():
        print("⏰ 当前不在开市时间，跳过报警")
        print("📊 开市时间：09:30-11:30, 13:00-15:00 (交易日)")
        print("\n✅ 完成！")
        exit(0)
    
    print("\n✅ 当前在开市时间")
    print("\n🔍 检查未发送警报...")
    alerts = get_unsent_alerts()
    
    if alerts:
        print(f"✅ 发现 {len(alerts)} 条未发送警报")
        
        # 格式化消息
        message = format_alert_message(alerts)
        
        # 发送
        print("\n📡 发送飞书警报...")
        success = send_feishu_alert(message)
        
        if success:
            # 标记已发送
            mark_alerts_sent(alerts)
            print(f"✅ 已标记 {len(alerts)} 条警报为已发送")
    else:
        print("✅ 无未发送警报")
    
    print("\n✅ 完成！")

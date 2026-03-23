#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询警报历史
"""

import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.expanduser('~/.openclaw/workspace/stock_database.db')

def query_alerts(limit=20):
    """查询最近警报"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT alert_type, stock_code, stock_name, alert_level, 
               message, current_price, trigger_value, created_at, is_sent
        FROM alert_history
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    print("=" * 80)
    print("🚨 警报历史记录")
    print("=" * 80)
    
    if not rows:
        print("\n暂无警报记录")
        return
    
    print(f"\n{'时间':<20} {'级别':<8} {'股票':<12} {'类型':<16} {'详情':<30}")
    print("-" * 80)
    
    for row in rows:
        alert_type, code, name, level, message, price, trigger, created, is_sent = row
        level_emoji = '🔴' if level == 'high' else '🟡'
        sent_status = '✅' if is_sent else '⏳'
        
        time_str = created.split(' ')[1] if created else '--'
        print(f"{time_str:<20} {level_emoji:<6} {name:<10} {alert_type:<16} {message[:28]:<30} {sent_status}")
    
    print("=" * 80)
    
    # 统计
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN alert_level = 'high' THEN 1 ELSE 0 END) as high_count,
            SUM(CASE WHEN is_sent = 1 THEN 1 ELSE 0 END) as sent_count
        FROM alert_history
    ''')
    
    stats = cursor.fetchone()
    conn.close()
    
    print(f"\n📊 统计:")
    print(f"  总警报数：{stats[0]}")
    print(f"  高危警报：{stats[1]}")
    print(f"  已发送：{stats[2]}")
    print(f"  待发送：{stats[0] - stats[2]}")

if __name__ == '__main__':
    query_alerts()

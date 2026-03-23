#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询交易建议历史和绩效统计
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.expanduser('~/.openclaw/workspace/stock_database.db')

def query_recommendations(stock_code=None, limit=10):
    """查询历史建议"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if stock_code:
        cursor.execute('''
            SELECT date, stock_code, stock_name, action, 
                   current_price, target_price, stop_loss, 
                   position_pct, confidence, profit_pct, change_pct
            FROM recommendations
            WHERE stock_code = ?
            ORDER BY date DESC, timestamp DESC
            LIMIT ?
        ''', (stock_code, limit))
    else:
        cursor.execute('''
            SELECT date, stock_code, stock_name, action, 
                   current_price, target_price, stop_loss, 
                   position_pct, confidence, profit_pct, change_pct
            FROM recommendations
            ORDER BY date DESC, timestamp DESC
            LIMIT ?
        ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def get_performance_summary():
    """获取绩效统计"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 总体统计
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN profit_pct > 0 THEN 1 ELSE 0 END) as wins,
            AVG(profit_pct) as avg_profit,
            MAX(profit_pct) as max_profit,
            MIN(profit_pct) as min_profit
        FROM recommendations
    ''')
    
    row = cursor.fetchone()
    
    # 按操作类型统计
    cursor.execute('''
        SELECT 
            action,
            COUNT(*) as count,
            AVG(profit_pct) as avg_profit
        FROM recommendations
        GROUP BY action
    ''')
    
    by_action = cursor.fetchall()
    conn.close()
    
    return {
        'total': row[0],
        'wins': row[1],
        'win_rate': row[1]/row[0]*100 if row[0] > 0 else 0,
        'avg_profit': row[2],
        'max_profit': row[3],
        'min_profit': row[4],
        'by_action': by_action
    }

def get_sentiment_history(limit=10):
    """获取市场情绪历史"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, score, level, sh_index, sz_index
        FROM sentiment_history
        ORDER BY date DESC, timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows

if __name__ == '__main__':
    print("=" * 80)
    print("📊 金融 Agent 绩效统计")
    print("=" * 80)
    
    # 总体绩效
    print("\n📈 总体绩效")
    perf = get_performance_summary()
    print(f"  总建议数：{perf['total']}")
    print(f"  盈利次数：{perf['wins']}")
    print(f"  胜率：{perf['win_rate']:.2f}%")
    print(f"  平均收益：{perf['avg_profit']:.2f}%")
    print(f"  最大盈利：{perf['max_profit']:.2f}%")
    print(f"  最大亏损：{perf['min_profit']:.2f}%")
    
    # 按操作类型
    print("\n📋 按操作类型统计")
    for action, count, avg_profit in perf['by_action']:
        print(f"  {action}: {count}次，平均收益 {avg_profit:.2f}%")
    
    # 最近建议
    print("\n📝 最近建议记录")
    rows = query_recommendations(limit=10)
    print(f"{'日期':<12} {'代码':<8} {'名称':<10} {'操作':<16} {'现价':>8} {'目标':>8} {'止损':>8} {'盈亏%':>10}")
    print("-" * 80)
    for row in rows:
        date, code, name, action, current, target, stop, position, confidence, profit, change = row
        print(f"{date:<12} {code:<8} {name:<10} {action:<16} {current:>8.2f} {target:>8.2f} {stop:>8.2f} {profit:>10.2f}%")
    
    # 情绪历史
    print("\n🌡️ 市场情绪历史")
    sentiment_rows = get_sentiment_history(limit=5)
    print(f"{'日期':<12} {'评分':>8} {'等级':<12} {'上证':>10} {'深证':>10}")
    print("-" * 60)
    for row in sentiment_rows:
        date, score, level, sh, sz = row
        print(f"{date:<12} {score:>8}/100 {level:<12} {sh:>10.2f} {sz:>10.2f}")
    
    print("\n" + "=" * 80)

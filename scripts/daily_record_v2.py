#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日交易建议记录 - 多数据源版本 v2.1
集成多数据源并行获取器 + 结构化报告生成器
"""

import sqlite3
import json
import os
import sys
from datetime import datetime

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_source_fetcher import MultiSourceFetcher
from structured_report import generate_trading_report

DB_PATH = os.path.expanduser('~/.openclaw/workspace/stock_database.db')
CONFIG_PATH = os.path.expanduser('~/.openclaw/workspace/config.json')

def load_config():
    """加载配置文件"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_sector(code):
    """获取股票所属板块"""
    sectors = {
        '000703': '石化化纤',
        '002358': '电力设备',
        '002498': '电线电缆',
        '002738': '锂电/资源',
        '601616': '电力设备',
        '601698': '卫星互联网'
    }
    return sectors.get(code, '未知')

def generate_recommendation(stock_data):
    """根据数据生成交易建议"""
    code = stock_data['code']
    profit_pct = stock_data['profit_pct']
    change_pct = stock_data['change_pct']
    inflow = stock_data.get('main_net_inflow', 0)
    current = stock_data['current']
    cost = stock_data['cost']
    
    # 策略逻辑
    if profit_pct > 50 and change_pct < -2:
        action = '🟡 持有/部分止盈'
        target = current * 1.08
        stop_loss = current * 0.88
        position = 50
        confidence = '中等'
        notes = '盈利丰厚，可减仓锁定利润'
    elif profit_pct < -5 and change_pct < -3:
        action = '🔴 减仓/止损'
        target = current * 1.15
        stop_loss = current * 0.92
        position = 30
        confidence = '中等'
        notes = '亏损状态，主力流出'
    elif profit_pct > 20:
        action = '🟡 持有'
        target = current * 1.10
        stop_loss = current * 0.90
        position = 70
        confidence = '中等'
        notes = '盈利安全垫厚，继续持有'
    elif profit_pct < 0:
        action = '🔴 减仓/观望'
        target = current * 1.20
        stop_loss = current * 0.85
        position = 30
        confidence = '低'
        notes = '亏损状态，设置止损'
    else:
        action = '🟡 持有'
        target = current * 1.10
        stop_loss = current * 0.90
        position = 60
        confidence = '中等'
        notes = '正常持有'
    
    # 特殊处理：中国卫通
    if code == '601698' and change_pct > 5:
        action = '🟢 持有/加仓'
        target = current * 1.06
        stop_loss = current * 0.91
        position = 80
        confidence = '高'
        notes = '逆势上涨，主力大幅流入'
    
    return {
        'action': action,
        'target_price': round(target, 2),
        'stop_loss': round(stop_loss, 2),
        'position_pct': position,
        'confidence': confidence,
        'notes': notes
    }

def save_to_database(date, timestamp, stocks_data, recommendations):
    """保存到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for stock, rec in zip(stocks_data, recommendations):
        # 检查是否已存在今日记录
        cursor.execute('''
            SELECT id FROM recommendations
            WHERE date = ? AND stock_code = ?
        ''', (date, stock['code']))
        
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有记录
            cursor.execute('''
                UPDATE recommendations SET
                    timestamp = ?,
                    action = ?,
                    target_price = ?,
                    stop_loss = ?,
                    position_pct = ?,
                    confidence = ?,
                    current_price = ?,
                    profit_pct = ?,
                    change_pct = ?,
                    main_net_inflow = ?,
                    notes = ?
                WHERE date = ? AND stock_code = ?
            ''', (
                timestamp, rec['action'], rec['target_price'], rec['stop_loss'],
                rec['position_pct'], rec['confidence'], stock['current'],
                stock['profit_pct'], stock['change_pct'], stock.get('main_net_inflow', 0),
                rec['notes'], date, stock['code']
            ))
            print(f"  ✏️  更新：{stock['code']} {stock['name']}")
        else:
            # 插入新记录
            cursor.execute('''
                INSERT INTO recommendations (
                    date, timestamp, stock_code, stock_name, action,
                    target_price, stop_loss, position_pct, confidence,
                    current_price, cost_basis, profit_pct, change_pct,
                    main_net_inflow, sector, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                date, timestamp, stock['code'], stock['name'], rec['action'],
                rec['target_price'], rec['stop_loss'], rec['position_pct'],
                rec['confidence'], stock['current'], stock['cost'],
                stock['profit_pct'], stock['change_pct'],
                stock.get('main_net_inflow', 0), get_sector(stock['code']),
                rec['notes']
            ))
            print(f"  ✅ 新增：{stock['code']} {stock['name']}")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("=" * 80)
    print("📊 每日交易建议记录 - 多数据源版本")
    print("=" * 80)
    
    date = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    print(f"\n📅 日期：{date}")
    print(f"⏰ 时间：{timestamp}")
    
    # 加载配置
    print("\n📂 加载配置...")
    config = load_config()
    stocks = config.get('portfolio', {}).get('stocks', [])
    print(f"✅ 持仓股票：{len(stocks)}只")
    
    # 多数据源获取
    print("\n📡 获取实时数据 (多数据源并行)...")
    fetcher = MultiSourceFetcher()
    results = fetcher.fetch_all()
    
    # 准备数据
    stocks_data = []
    for result in results:
        if result['validated']:
            data = result['validated']
            stocks_data.append({
                'code': result['code'],
                'name': result['name'],
                'cost': result['cost'],
                'current': data['current'],
                'change_pct': data['change_pct'],
                'profit_pct': ((data['current'] - result['cost']) / result['cost'] * 100),
                'main_net_inflow': data.get('main_net_inflow', 0),
            })
    
    print(f"✅ 获取成功：{len(stocks_data)}只")
    
    # 生成建议
    print("\n📝 生成交易建议...")
    recommendations = [generate_recommendation(stock) for stock in stocks_data]
    
    # 打印建议
    print("\n💡 今日建议:")
    for stock, rec in zip(stocks_data, recommendations):
        print(f"  {stock['code']} {stock['name']}: {rec['action']} (仓位{rec['position_pct']}%)")
    
    # 保存
    print("\n💾 保存到数据库...")
    save_to_database(date, timestamp, stocks_data, recommendations)
    
    # 生成结构化报告
    print("\n📊 生成结构化报告...")
    market_sentiment = {'score': 50, 'level': '中性'}  # TODO: 从实际数据获取
    report = generate_trading_report(stocks_data, recommendations, market_sentiment)
    
    # 保存报告
    reports_dir = os.path.expanduser('~/.openclaw/workspace/reports')
    os.makedirs(reports_dir, exist_ok=True)
    report_file = os.path.join(reports_dir, f'structured_report_{date}.md')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已保存：{report_file}")
    print("\n✅ 完成！")

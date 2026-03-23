#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记录每日交易建议到数据库
在每日 10:00 分析完成后自动调用
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.expanduser('~/.openclaw/workspace/stock_database.db')

# 持仓配置
CONFIG_PATH = os.path.expanduser('~/.openclaw/workspace/config.json')

def load_config():
    """加载配置文件"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_stock_data():
    """获取股票实时数据"""
    import requests
    
    config = load_config()
    stocks = config.get('portfolio', {}).get('stocks', [])
    
    results = []
    for stock in stocks:
        code = stock['code']
        market = stock.get('market', 'sh' if code.startswith('6') else 'sz')
        secid = f'1.{code}' if market == 'sh' else f'0.{code}'
        
        url = f'https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f44,f169,f170,f137'
        
        try:
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if data.get('rc') == 0 and data.get('data'):
                d = data['data']
                current = d.get('f43', 0) / 100
                change_pct = d.get('f170', 0) / 100
                main_net_inflow = d.get('f137', 0)
                
                cost = stock.get('cost', 0)
                profit_pct = ((current - cost) / cost * 100) if cost > 0 else 0
                
                results.append({
                    'code': code,
                    'name': stock.get('name', ''),
                    'cost': cost,
                    'current': current,
                    'change_pct': change_pct,
                    'profit_pct': profit_pct,
                    'main_net_inflow': main_net_inflow,
                    'market': market
                })
        except Exception as e:
            print(f"获取 {code} 失败：{e}")
    
    return results

def generate_recommendation(stock_data):
    """根据数据生成交易建议"""
    code = stock_data['code']
    profit_pct = stock_data['profit_pct']
    change_pct = stock_data['change_pct']
    inflow = stock_data['main_net_inflow']
    
    # 简单策略
    if profit_pct > 50 and change_pct < -2:
        action = '🟡 持有/部分止盈'
        target = stock_data['current'] * 1.08
        stop_loss = stock_data['current'] * 0.88
        position = 50
        confidence = '中等'
    elif profit_pct < -5 and change_pct < -3:
        action = '🔴 减仓/止损'
        target = stock_data['current'] * 1.15
        stop_loss = stock_data['current'] * 0.92
        position = 30
        confidence = '中等'
    elif profit_pct > 20:
        action = '🟡 持有'
        target = stock_data['current'] * 1.10
        stop_loss = stock_data['current'] * 0.90
        position = 70
        confidence = '中等'
    elif profit_pct < 0:
        action = '🔴 减仓/观望'
        target = stock_data['current'] * 1.20
        stop_loss = stock_data['current'] * 0.85
        position = 30
        confidence = '低'
    else:
        action = '🟡 持有'
        target = stock_data['current'] * 1.10
        stop_loss = stock_data['current'] * 0.90
        position = 60
        confidence = '中等'
    
    # 特殊处理：中国卫通
    if code == '601698' and change_pct > 5:
        action = '🟢 持有/加仓'
        target = stock_data['current'] * 1.06
        stop_loss = stock_data['current'] * 0.91
        position = 80
        confidence = '高'
    
    return {
        'action': action,
        'target_price': round(target, 2),
        'stop_loss': round(stop_loss, 2),
        'position_pct': position,
        'confidence': confidence
    }

def save_to_database(date, timestamp, stocks_data, recommendations):
    """保存到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for stock, rec in zip(stocks_data, recommendations):
        cursor.execute('''
            INSERT INTO recommendations (
                date, timestamp, stock_code, stock_name, action,
                target_price, stop_loss, position_pct, confidence,
                current_price, cost_basis, profit_pct, change_pct,
                main_net_inflow, sector, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            date,
            timestamp,
            stock['code'],
            stock['name'],
            rec['action'],
            rec['target_price'],
            rec['stop_loss'],
            rec['position_pct'],
            rec['confidence'],
            stock['current'],
            stock['cost'],
            stock['profit_pct'],
            stock['change_pct'],
            stock['main_net_inflow'],
            get_sector(stock['code']),
            rec['action']
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ 已保存 {len(recommendations)} 条建议")

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

if __name__ == '__main__':
    print("📊 记录每日交易建议")
    print("=" * 50)
    
    date = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 获取数据
    print("\n📈 获取股票数据...")
    stocks_data = get_stock_data()
    print(f"✅ 获取到 {len(stocks_data)} 只股票")
    
    # 生成建议
    print("\n📝 生成交易建议...")
    recommendations = [generate_recommendation(stock) for stock in stocks_data]
    
    # 打印建议
    for stock, rec in zip(stocks_data, recommendations):
        print(f"  {stock['code']} {stock['name']}: {rec['action']}")
    
    # 保存
    print("\n💾 保存到数据库...")
    save_to_database(date, timestamp, stocks_data, recommendations)
    
    print("\n✅ 完成！")

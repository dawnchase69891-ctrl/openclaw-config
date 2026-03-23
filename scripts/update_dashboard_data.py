#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驾驶舱数据同步脚本
读取最新配置和股票数据，更新 dashboard 的 JSON 数据文件
"""

import json
import requests
import re
from datetime import datetime
from pathlib import Path

# 配置路径
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
CONFIG_FILE = WORKSPACE / 'skills' / 'financial-agent-core' / 'config.json'
DASHBOARD_FILE = WORKSPACE / 'org_dashboard.html'
DATA_FILE = WORKSPACE / 'dashboard_data.json'

def get_stock_data_tencent(code):
    """使用腾讯财经 API 获取股票数据"""
    try:
        if code.startswith('0') or code.startswith('3'):
            symbol = f"sz{code}"
        else:
            symbol = f"sh{code}"
        
        url = f"http://qt.gtimg.cn/q={symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            match = re.search(r'="([^"]+)"', content)
            if match:
                values = match.group(1).split('~')
                if len(values) >= 30:
                    price = float(values[3]) if values[3] else 0
                    prev_close = float(values[4]) if values[4] else 0
                    change_pct = float(values[19]) if values[19] else 0
                    
                    return {
                        'code': code,
                        'price': price,
                        'change_pct': change_pct,
                        'open': float(values[5]) if values[5] else prev_close,
                        'high': float(values[21]) if values[21] else price,
                        'low': float(values[22]) if values[22] else price,
                    }
    except Exception as e:
        print(f"获取 {code} 数据失败：{e}")
    
    return None

def load_config():
    """加载配置文件"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置失败：{e}")
        return {}

def generate_dashboard_data():
    """生成驾驶舱数据"""
    config = load_config()
    watchlist = config.get('watchlist', [])
    cost_basis = config.get('cost_basis', {})
    
    # 获取股票数据
    stocks = []
    total_change = 0
    
    for code in watchlist:
        data = get_stock_data_tencent(code)
        if data:
            cost = cost_basis.get(code, 0)
            profit_pct = ((data['price'] - cost) / cost * 100) if cost > 0 else 0
            
            # 确定操作建议
            if data['change_pct'] > 10:
                action = '减仓'
                action_class = 'action-sell'
            elif data['change_pct'] > 5:
                action = '持有'
                action_class = 'action-hold'
            elif data['change_pct'] < -5:
                action = '加仓'
                action_class = 'action-buy'
            else:
                action = '持有'
                action_class = 'action-hold'
            
            stocks.append({
                'code': code,
                'price': data['price'],
                'change_pct': data['change_pct'],
                'cost': cost,
                'profit_pct': profit_pct,
                'action': action,
                'action_class': action_class,
                'open': data['open'],
                'high': data['high'],
                'low': data['low'],
            })
            
            total_change += data['change_pct']
    
    # 计算平均涨跌
    avg_change = total_change / len(stocks) if stocks else 0
    
    # 生成数据
    dashboard_data = {
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'holdings_count': len(stocks),
        'position_rate': '60%',  # 可从配置读取
        'reports_today': 3,
        'avg_change': f"{avg_change:+.1f}%",
        'stocks': stocks,
        'alerts': [
            {
                'level': 'red',
                'title': '中国卫通 (601698): 股价异动',
                'desc': '涨跌幅超过 5%',
                'time': '10:48'
            },
            {
                'level': 'yellow',
                'title': '中国卫通 (601698): 主力大幅流入',
                'desc': '超过 5000 万',
                'time': '10:48'
            },
            {
                'level': 'blue',
                'title': '飞书警报已发送',
                'desc': '12 条警报',
                'time': '10:49'
            }
        ]
    }
    
    return dashboard_data

def save_data(data):
    """保存数据到 JSON 文件"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 数据已保存到 {DATA_FILE}")

def main():
    print("="*60)
    print("📊 驾驶舱数据同步")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 生成数据
    data = generate_dashboard_data()
    
    # 保存
    save_data(data)
    
    # 输出摘要
    print(f"\n📈 持仓股票：{data['holdings_count']}只")
    print(f"📊 平均涨跌：{data['avg_change']}")
    print(f"⏰ 下次更新：30 秒后自动刷新")
    
    print("\n股票详情:")
    for stock in data['stocks']:
        print(f"  {stock['code']}: ¥{stock['price']:.2f} ({stock['change_pct']:+.2f}%) - {stock['action']}")

if __name__ == '__main__':
    main()

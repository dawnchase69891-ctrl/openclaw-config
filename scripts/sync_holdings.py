#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓数据同步脚本
从东方财富 API 获取最新股价，更新飞书多维表格持仓表
"""

import subprocess
import json
import sys
sys.path.insert(0, '/home/uos/.openclaw/workspace')

# 配置
APP_TOKEN = "UdRjbT10baQ5zAsa6zpcrsAbnIQ"
TABLE_ID = "tblIIll4K93jYWvt"
HOLDINGS = [
    {"code": "002285", "name": "世联行", "shares": 6000, "cost": 3.05, "record_id": "recve8fs5VnyWd"},
    {"code": "002256", "name": "兆新股份", "shares": 4000, "cost": 4.02, "record_id": "recve8fs5VcEJ5"},
    {"code": "000572", "name": "海马汽车", "shares": 3000, "cost": 6.35, "record_id": "recve8fs5VNvLn"},
]

def get_stock_prices():
    """从东方财富 API 获取股价"""
    codes = ",".join(["0.{}".format(h['code']) for h in HOLDINGS])
    url = "http://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&secids={}&fields=f12,f14,f2,f3".format(codes)
    
    import urllib2
    request = urllib2.Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    response = urllib2.urlopen(request, timeout=10)
    result_stdout = response.read()
    
    data = json.loads(result_stdout)
    prices = {}
    for item in data.get('data', {}).get('diff', []):
        code = item.get('f12', '')
        price = float(item.get('f2', 0))
        change = float(item.get('f3', 0))
        prices[code] = {"price": price, "change": change}
    
    return prices

def sync_to_feishu(prices):
    """更新飞书多维表格"""
    from feishu_bitable_app_table_record import feishu_bitable_app_table_record
    
    for holding in HOLDINGS:
        code = holding["code"]
        if code not in prices:
            print(u"⚠️ {} 价格获取失败".format(holding['name']))
            continue
        
        price = prices[code]["price"]
        shares = holding["shares"]
        cost = holding["cost"]
        
        # 计算盈亏
        profit_pct = round((price - cost) / cost * 100, 2)
        profit_amt = round((price - cost) * shares, 2)
        market_value = round(price * shares, 2)
        
        # 更新飞书
        print(u"📈 {}: ¥{} ({:+.2f}%)".format(holding['name'], price, profit_pct))
        
        # 调用飞书 API 更新
        # 这里需要用 subprocess 调用 openclaw 命令或直接调用 API

if __name__ == "__main__":
    print("🔄 开始同步持仓数据...")
    prices = get_stock_prices()
    sync_to_feishu(prices)
    print("✅ 同步完成")
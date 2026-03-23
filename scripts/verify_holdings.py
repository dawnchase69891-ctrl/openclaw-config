#!/usr/bin/env python3
"""
持仓数据校验脚本
对比持仓表数据与实际行情，输出差异报告
"""

import subprocess
import json

HOLDINGS = [
    {"code": "002285", "name": "世联行", "shares": 6000, "cost": 3.05},
    {"code": "002256", "name": "兆新股份", "shares": 4000, "cost": 4.02},
    {"code": "000572", "name": "海马汽车", "shares": 3000, "cost": 6.35},
]

def get_real_prices():
    """获取实时股价"""
    codes = ",".join([f"0.{h['code']}" for h in HOLDINGS])
    url = f"http://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&secids={codes}&fields=f12,f14,f2,f3"
    
    result = subprocess.run(
        ["curl", "-s", url],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    data = json.loads(result.stdout)
    prices = {}
    for item in data.get('data', {}).get('diff', []):
        code = item.get('f12', '')
        price = float(item.get('f2', 0))
        change = float(item.get('f3', 0))
        prices[code] = {"price": price, "change": change}
    
    return prices

def verify():
    """校验持仓数据"""
    print("🔍 持仓数据校验报告")
    print("=" * 50)
    
    prices = get_real_prices()
    total_value = 0
    total_profit = 0
    
    for h in HOLDINGS:
        code = h["code"]
        if code not in prices:
            print(f"❌ {h['name']}: 无法获取价格")
            continue
        
        real_price = prices[code]["price"]
        shares = h["shares"]
        cost = h["cost"]
        
        profit_pct = (real_price - cost) / cost * 100
        profit_amt = (real_price - cost) * shares
        market_value = real_price * shares
        
        total_value += market_value
        total_profit += profit_amt
        
        status = "✅" if profit_pct >= 0 else "⚠️"
        print(f"{status} {h['name']}: 成本¥{cost} → 现价¥{real_price:.2f} ({profit_pct:+.2f}%)")
    
    print("=" * 50)
    print(f"💰 总市值: ¥{total_value:,.2f}")
    print(f"📊 总盈亏: ¥{total_profit:+,.2f}")

if __name__ == "__main__":
    verify()
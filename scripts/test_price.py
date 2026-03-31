#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试价格服务（使用简化方式）
"""

import sys
sys.path.insert(0, '/home/uos/.openclaw/workspace/scripts/lib')

from price_service import PriceService

print("📊 测试价格获取（新浪财经）...")
service = PriceService(use_tushare=False)

test_codes = ['601698', '601616', '002738', '000703']

for code in test_codes:
    price = service.get_price(code)
    if price is not None and price > 0:
        print(f"✅ {code}: ¥{price:.2f}")
    else:
        print(f"❌ {code}: 获取失败或价格为 0")

print("\n✅ 测试完成！")
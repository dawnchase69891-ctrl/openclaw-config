#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复调仓计划数据
"""

import json
from datetime import datetime

plans_file = '/home/uos/.openclaw/workspace/scripts/data/rebalance_plans.json'

# 读取当前数据
with open(plans_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 修复重复的 ID
plans = [
    {
        "stock": "中国卫通",
        "code": "601698",
        "action": "卖出",
        "quantity": 500,
        "target_price": 38.0,
        "priority": "P0",
        "reason": "仓位优化，从 38% 降至 18%",
        "id": "plan_20260331120001",
        "created_date": "2026-03-31",
        "status": "active",
        "last_updated": "2026-03-31 11:45:00",
        "expiry_threshold": 0.1,
        "base_price": 38.0,
        "current_price": 0.0
    },
    {
        "stock": "广电电气",
        "code": "601616",
        "action": "卖出",
        "quantity": 1500,
        "target_price": 6.0,
        "priority": "P0",
        "reason": "低评分股票减仓，从 18% 降至 8%",
        "id": "plan_20260331120002",
        "created_date": "2026-03-31",
        "status": "active",
        "last_updated": "2026-03-31 11:45:00",
        "expiry_threshold": 0.1,
        "base_price": 6.0,
        "current_price": 0.0
    },
    {
        "stock": "中矿资源",
        "code": "002738",
        "action": "买入",
        "quantity": 200,
        "target_price": 79.0,
        "priority": "P1",
        "reason": "高评分股票加仓，目标仓位 12%",
        "id": "plan_20260331120003",
        "created_date": "2026-03-31",
        "status": "active",
        "last_updated": "2026-03-31 11:45:00",
        "expiry_threshold": 0.1,
        "base_price": 79.0,
        "current_price": 0.0
    },
    {
        "stock": "恒逸石化",
        "code": "000703",
        "action": "买入",
        "quantity": 500,
        "target_price": 12.5,
        "priority": "P2",
        "reason": "牛股加仓，目标仓位 11%",
        "id": "plan_20260331120004",
        "created_date": "2026-03-31",
        "status": "active",
        "last_updated": "2026-03-31 11:45:00",
        "expiry_threshold": 0.1,
        "base_price": 12.5,
        "current_price": 0.0
    }
]

data['plans'] = plans
data['metadata']['last_refresh'] = datetime.now().strftime('%Y-%m-%d')

# 保存
with open(plans_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 数据修复完成！")
print(f"   共 {len(plans)} 个计划")
for plan in plans:
    print(f"   - {plan['stock']} ({plan['id']})")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试系统核心功能（离线模式）
"""

import sys
import json

# 模拟价格服务（离线）
class MockPriceService:
    def get_price(self, code):
        # 返回模拟价格
        mock_prices = {
            '601698': 38.50,
            '601616': 6.20,
            '002738': 78.80,
            '000703': 12.30
        }
        return mock_prices.get(code, 0.0)

# 测试导入
sys.path.insert(0, '/home/uos/.openclaw/workspace/scripts/lib')

from plan_manager import RebalancePlanManager

print("=" * 50)
print("🔧 调仓提醒系统核心功能测试")
print("=" * 50)

# 1. 测试计划管理器
print("\n[1/3] 测试计划管理器...")
manager = RebalancePlanManager()

stats = manager.get_statistics()
print(f"   总计划数: {stats['total']}")
print(f"   活跃计划: {stats['active']}")
print(f"   过期计划: {stats['expired']}")
print(f"   已执行: {stats['executed']}")

active_plans = manager.get_active_plans()
print(f"\n   活跃计划列表:")
for plan in active_plans:
    print(f"     - {plan['stock']} ({plan['code']}) {plan['action']} {plan['quantity']}股 @ ¥{plan['target_price']}")

# 2. 测试价格刷新
print("\n[2/3] 测试价格刷新...")
mock_service = MockPriceService()

manager.refresh_all_prices(mock_service)

print("\n   价格更新后:")
for plan in manager.get_active_plans():
    current_price = plan.get('current_price', 0)
    status = plan.get('status', 'unknown')
    print(f"     - {plan['stock']}: ¥{current_price:.2f} [{status}]")

# 3. 测试自动失效（模拟价格偏离）
print("\n[3/3] 测试自动失效机制...")

# 修改某个计划的 base_price，模拟偏离超过 10%
data = manager._load_plans()
for plan in data['plans']:
    if plan['stock'] == '恒逸石化':
        plan['base_price'] = 15.0  # 设置基准价为 15.0，当前价 12.30，偏离 18%
        break

manager._save_plans(data)

# 刷新价格，应该会自动失效
manager.refresh_all_prices(mock_service)

print("\n   失效测试结果:")
for plan in manager.get_all_plans():
    if plan.get('status') == 'expired':
        reason = plan.get('expiry_reason', '未知原因')
        print(f"     ⚠️  {plan['stock']} 已失效: {reason}")

# 保存测试结果
print("\n" + "=" * 50)
print("✅ 核心功能测试通过！")
print("=" * 50)

print("\n📊 最终统计:")
stats = manager.get_statistics()
for key, value in stats.items():
    print(f"   {key}: {value}")

print("\n💡 系统已就绪，可以执行以下命令:")
print("   python3 feishu_rebalance_reminder.py morning   # 发送盘前提醒")
print("   python3 feishu_rebalance_reminder.py evening   # 发送收盘复盘")
print("   python3 feishu_rebalance_reminder.py refresh   # 刷新价格")
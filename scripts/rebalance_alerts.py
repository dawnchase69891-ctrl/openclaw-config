#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票调仓提醒脚本
每日检查持仓股票价格，发送飞书提醒
"""

import sys
import json
from datetime import datetime

# 添加路径
sys.path.insert(0, '/home/uos/.openclaw/workspace/skills/a-stock-monitor/scripts')

# 提醒配置
ALERTS = [
    {
        'stock': '中国卫通',
        'code': '601698',
        'type': 'SELL',
        'target_price': 38.00,
        'quantity': 500,
        'reason': '仓位优化，从 38% 降至 18%',
        'priority': 'P0'
    },
    {
        'stock': '广电电气',
        'code': '601616',
        'type': 'SELL',
        'target_price': 6.00,
        'quantity': 1500,
        'reason': '低评分股票减仓，从 18% 降至 8%',
        'priority': 'P0'
    },
    {
        'stock': '中矿资源',
        'code': '002738',
        'type': 'BUY',
        'target_price': 79.00,
        'quantity': 200,
        'reason': '高评分股票加仓，目标仓位 12%',
        'priority': 'P1'
    },
    {
        'stock': '中矿资源',
        'code': '002738',
        'type': 'BUY',
        'target_price': 76.00,
        'quantity': 300,
        'reason': '分批建仓，降低均价',
        'priority': 'P1'
    },
    {
        'stock': '恒逸石化',
        'code': '000703',
        'type': 'BUY',
        'target_price': 12.50,
        'quantity': 500,
        'reason': '牛股加仓，目标仓位 11%',
        'priority': 'P2'
    }
]

def check_prices():
    """检查股票价格，触发提醒"""
    print("=" * 60)
    print("📱 股票调仓价格检查")
    print(f"⏰ 检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # TODO: 接入实时价格数据
    # 这里简化处理，实际应该调用价格 API
    
    triggered_alerts = []
    
    for alert in ALERTS:
        # 模拟价格检查 (实际应该获取实时价格)
        print(f"\n检查：{alert['stock']} ({alert['code']})")
        print(f"  操作：{'卖出' if alert['type'] == 'SELL' else '买入'} {alert['quantity']} 股")
        print(f"  目标价：¥{alert['target_price']}")
        print(f"  优先级：{alert['priority']}")
        
        # 这里应该添加价格比较逻辑
        # if current_price >= alert['target_price'] (for SELL)
        # if current_price <= alert['target_price'] (for BUY)
        #     triggered_alerts.append(alert)
    
    print("\n" + "=" * 60)
    print(f"✅ 检查完成，触发 {len(triggered_alerts)} 个提醒")
    
    return triggered_alerts

def send_feishu_alert(alert):
    """发送飞书提醒"""
    action_text = '卖出' if alert['type'] == 'SELL' else '买入'
    emoji = '🔴' if alert['type'] == 'SELL' else '🟢'
    
    message = f"""
{emoji} {alert['stock']} ({alert['code']}) 调仓提醒

操作：{action_text} {alert['quantity']} 股
目标价：¥{alert['target_price']}
优先级：{alert['priority']}

理由：{alert['reason']}

⏰ 提醒时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    print(f"\n📱 准备发送飞书提醒:")
    print(message)
    
    # TODO: 调用飞书 API 发送消息
    # 可以使用现有的 feishu_alert.py 脚本
    
    return True

def main():
    """主函数"""
    triggered = check_prices()
    
    for alert in triggered:
        send_feishu_alert(alert)
    
    print("\n✅ 所有提醒已处理")

if __name__ == '__main__':
    main()

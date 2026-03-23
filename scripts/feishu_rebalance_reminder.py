#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票调仓飞书提醒脚本
发送盘前提醒、价格提醒、收盘复盘到飞书
"""

import requests
import json
from datetime import datetime
import sys

# 飞书 Webhook
FEISHU_WEBHOOK = 'https://open.feishu.cn/open-apis/bot/v2/hook/475f79a4-dffc-4e4f-82e8-d483581b86ca'

# 调仓配置
REBALANCE_PLAN = [
    {
        'stock': '中国卫通',
        'code': '601698',
        'action': '卖出',
        'quantity': 500,
        'target_price': 38.00,
        'priority': 'P0',
        'reason': '仓位优化，从 38% 降至 18%'
    },
    {
        'stock': '中国卫通',
        'code': '601698',
        'action': '卖出',
        'quantity': 500,
        'target_price': 38.00,
        'priority': 'P0',
        'reason': '仓位优化，从 38% 降至 18% (第二笔)'
    },
    {
        'stock': '广电电气',
        'code': '601616',
        'action': '卖出',
        'quantity': 1500,
        'target_price': 6.00,
        'priority': 'P0',
        'reason': '低评分股票减仓，从 18% 降至 8%'
    },
    {
        'stock': '广电电气',
        'code': '601616',
        'action': '卖出',
        'quantity': 1500,
        'target_price': 6.00,
        'priority': 'P0',
        'reason': '低评分股票减仓，从 18% 降至 8% (第二笔)'
    },
    {
        'stock': '中矿资源',
        'code': '002738',
        'action': '买入',
        'quantity': 200,
        'target_price': 79.00,
        'priority': 'P1',
        'reason': '高评分股票加仓，目标仓位 12%'
    },
    {
        'stock': '中矿资源',
        'code': '002738',
        'action': '买入',
        'quantity': 300,
        'target_price': 76.00,
        'priority': 'P1',
        'reason': '分批建仓，降低均价'
    },
    {
        'stock': '恒逸石化',
        'code': '000703',
        'action': '买入',
        'quantity': 500,
        'target_price': 12.50,
        'priority': 'P2',
        'reason': '牛股加仓，目标仓位 11%'
    }
]

def send_feishu_message(msg_type, content):
    """发送飞书消息"""
    payload = {
        'msg_type': msg_type,
        'content': content
    }
    
    try:
        response = requests.post(
            FEISHU_WEBHOOK,
            json=payload,
            timeout=30
        )
        result = response.json()
        
        if result.get('code') == 0 or result.get('StatusCode') == 0:
            print(f"✅ 飞书消息发送成功")
            return True
        else:
            print(f"❌ 飞书消息发送失败：{result}")
            return False
    except Exception as e:
        print(f"❌ 发送异常：{e}")
        return False

def send_morning_reminder():
    """发送盘前提醒"""
    today = datetime.now().strftime('%Y-%m-%d')
    weekday = datetime.now().strftime('%A')
    
    text = f"""📊 调仓盘前提醒 ({today})

⏰ 开市时间：09:30-11:30, 13:00-15:00

━━━━━━━━━━━━━━━━━━━━

📋 今日操作计划:

【优先执行 P0】
"""
    
    # 添加 P0 优先级操作
    p0_items = [x for x in REBALANCE_PLAN if x['priority'] == 'P0']
    for item in p0_items:
        emoji = '🔴' if item['action'] == '卖出' else '🟢'
        text += f"{emoji} {item['stock']} {item['action']} {item['quantity']}股 @ ¥{item['target_price']}+\n"
    
    text += """
【择机执行 P1/P2】
"""
    
    # 添加其他操作
    other_items = [x for x in REBALANCE_PLAN if x['priority'] not in ['P0']]
    for item in other_items:
        emoji = '🟡' if item['priority'] == 'P1' else '🟢'
        text += f"{emoji} {item['stock']} {item['action']} {item['quantity']}股 @ ¥{item['target_price']}\n"
    
    text += """
━━━━━━━━━━━━━━━━━━━━

💡 操作提示:
1. 优先执行 P0 操作 (减仓)
2. P1/P2 操作可逢低分批买入
3. 注意控制每笔交易成本

📱 盘中价格触及会自动提醒
📱 15:30 发送执行复盘

祝投资顺利！🐎"""
    
    content = {
        'text': text
    }
    
    print(f"📱 发送盘前提醒...")
    return send_feishu_message('text', content)

def send_price_alert(stock, code, action, quantity, current_price, target_price):
    """发送价格提醒"""
    emoji = '🔴' if action == '卖出' else '🟢'
    
    text = f"""{emoji} {stock} ({code}) 价格提醒

现价：¥{current_price}
操作：{action} {quantity} 股
目标价：¥{target_price}

💡 建议：价格已到达目标区间，可考虑执行操作。

⏰ 提醒时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"""
    
    content = {
        'text': text
    }
    
    print(f"📱 发送价格提醒...")
    return send_feishu_message('text', content)

def send_evening_review():
    """发送收盘复盘"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    text = f"""📈 调仓执行复盘 ({today})

━━━━━━━━━━━━━━━━━━━━

✅ 请确认今日操作:

【减持操作】
□ 中国卫通 卖出 500 股
□ 广电电气 卖出 1,500 股

【增持操作】
□ 中矿资源 买入 200 股
□ 恒逸石化 买入 500 股

━━━━━━━━━━━━━━━━━━━━

💬 请回复今日执行情况:
• 已完成的操作
• 未完成的原因
• 明日计划

📊 累计统计将在本周五汇总。

晚安！🐎"""
    
    content = {
        'text': text
    }
    
    print(f"📱 发送收盘复盘...")
    return send_feishu_message('text', content)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python3 feishu_rebalance_reminder.py <morning|price|evening>")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'morning':
        success = send_morning_reminder()
    elif action == 'price':
        # 价格提醒需要参数
        if len(sys.argv) < 7:
            print("用法：python3 feishu_rebalance_reminder.py price <stock> <code> <action> <quantity> <current_price> <target_price>")
            sys.exit(1)
        stock = sys.argv[2]
        code = sys.argv[3]
        action_type = sys.argv[4]
        quantity = int(sys.argv[5])
        current_price = float(sys.argv[6])
        target_price = float(sys.argv[7]) if len(sys.argv) > 7 else 0
        success = send_price_alert(stock, code, action_type, quantity, current_price, target_price)
    elif action == 'evening':
        success = send_evening_review()
    else:
        print(f"未知操作：{action}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

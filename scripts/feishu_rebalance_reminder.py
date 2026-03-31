#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票调仓飞书提醒脚本（v3.0）
重构版本：集成动态价格和自动失效机制

特性:
1. 盘前提醒: 读取JSON计划 → 获取实时价格 → 过滤过期建议 → 发送提醒
2. 价格监控: 实时价格触及目标时提醒
3. 收盘复盘: 收盘复盘 + 更新计划状态
4. 自动失效: 价格偏离超过10%的建议自动标记为 expired
"""

import requests
import json
from datetime import datetime
import sys
import os

# 添加 scripts 目录到路径
sys.path.append('/home/uos/.openclaw/workspace/scripts')

# 导入价格服务函数（按照任务要求）
from lib.price_service import get_realtime_price, get_batch_prices_optimized, check_price_deviation

# 飞书 Webhook
FEISHU_WEBHOOK = 'https://open.feishu.cn/open-apis/bot/v2/hook/475f79a4-dffc-4e4f-82e8-d483581b86ca'

# 数据文件路径
PLANS_FILE = '/home/uos/.openclaw/workspace/data/rebalance_plans.json'
HISTORY_FILE = '/home/uos/.openclaw/workspace/data/rebalance_history.json'


def load_plans():
    """加载调仓计划"""
    try:
        with open(PLANS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('plans', [])
    except Exception as e:
        print(f"❌ 加载计划文件失败: {e}")
        return []


def save_plans(plans):
    """保存调仓计划"""
    try:
        with open(PLANS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'plans': plans,
                'metadata': {
                    'last_refresh': datetime.now().strftime('%Y-%m-%d'),
                    'version': '3.0'
                }
            }, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存计划文件失败: {e}")
        return False


def get_active_plans(plans=None):
    """获取活跃计划（status=active）"""
    if plans is None:
        plans = load_plans()
    return [p for p in plans if p.get('status') == 'active']


def get_expired_plans(plans=None):
    """获取过期计划（status=expired）"""
    if plans is None:
        plans = load_plans()
    return [p for p in plans if p.get('status') == 'expired']


def update_plan_price(plan, current_price):
    """
    更新计划的价格并检查是否失效

    Args:
        plan: 计划字典（会被修改）
        current_price: 当前价格

    Returns:
        bool: 是否需要失效
    """
    plan['current_price'] = current_price
    plan['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 检查价格偏离度
    base_price = plan.get('base_price', plan.get('target_price', 0))
    threshold = plan.get('expiry_threshold', 0.10)

    if base_price > 0 and current_price > 0:
        is_exceeded, deviation = check_price_deviation(current_price, base_price, threshold)

        if is_exceeded:
            plan['status'] = 'expired'
            plan['expiry_reason'] = f'价格偏离 {deviation*100:.1f}% 超过阈值 {threshold*100:.0f}%'
            plan['expiry_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"⚠️  {plan['stock']} 计划已失效: {plan['expiry_reason']}")
            return True

    return False


def refresh_all_prices(plans=None):
    """
    刷新所有计划的价格并检查失效

    Args:
        plans: 计划列表（可选）

    Returns:
        更新后的计划列表
    """
    if plans is None:
        plans = load_plans()

    active_plans = get_active_plans(plans)

    if not active_plans:
        print("ℹ️  没有活跃计划需要刷新价格")
        return plans

    # 提取所有股票代码
    codes = [p.get('code') for p in active_plans if p.get('code')]
    codes = list(filter(None, codes))

    if not codes:
        print("ℹ️  没有有效的股票代码")
        return plans

    # 批量获取价格
    print(f"🔄 正在获取 {len(codes)} 只股票的实时价格...")
    prices = get_batch_prices_optimized(codes)

    # 更新每个计划的价格
    for plan in active_plans:
        code = plan.get('code')
        if code and code in prices:
            current_price = prices[code]
            if current_price is not None:
                update_plan_price(plan, current_price)
                print(f"✅ {plan['stock']} ({code}) 价格已更新: ¥{current_price:.2f}")
            else:
                print(f"❌ {plan['stock']} ({code}) 价格获取失败")

    return plans


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
    """
    发送盘前提醒（morning 模式）
    流程：读取计划 → 获取实时价格 → 过滤过期建议 → 发送提醒
    """
    print("📊 开始准备盘前提醒...")

    # 1. 读取计划
    plans = load_plans()

    # 2. 刷新价格并检查失效
    plans = refresh_all_prices(plans)
    save_plans(plans)  # 保存更新后的计划

    # 3. 获取活跃和过期计划
    active_plans = get_active_plans(plans)
    expired_plans = get_expired_plans(plans)

    today = datetime.now().strftime('%Y-%m-%d')

    # 构建消息
    text = f"""📊 调仓盘前提醒 ({today})

⏰ 开市时间：09:30-11:30, 13:00-15:00

━━━━━━━━━━━━━━━━━━━━

📋 今日活跃计划 ({len(active_plans)} 个):

【优先执行 P0】
"""

    # 添加 P0 优先级操作
    p0_items = [x for x in active_plans if x['priority'] == 'P0']
    for item in p0_items:
        emoji = '🔴' if item['action'] == '卖出' else '🟢'
        current_price = item.get('current_price', 0)
        price_info = f"现价 ¥{current_price:.2f} | " if current_price > 0 else ""
        text += f"{emoji} {item['stock']} {item['action']} {item['quantity']}股 @ ¥{item['target_price']}\n"
        text += f"   └─ {price_info}{item['reason']}\n"

    text += "\n【择机执行 P1/P2】\n"

    # 添加其他操作
    other_items = [x for x in active_plans if x['priority'] not in ['P0']]
    for item in other_items:
        emoji = '🟡' if item['priority'] == 'P1' else '🟢'
        current_price = item.get('current_price', 0)
        price_info = f"现价 ¥{current_price:.2f} | " if current_price > 0 else ""
        text += f"{emoji} {item['stock']} {item['action']} {item['quantity']}股 @ ¥{item['target_price']}\n"
        text += f"   └─ {price_info}{item['reason']}\n"

    # 添加过期计划提示
    if expired_plans:
        text += f"\n⚠️ 已失效计划 ({len(expired_plans)} 个):\n"
        for item in expired_plans:
            reason = item.get('expiry_reason', '已失效')
            text += f"   ❌ {item['stock']} ({reason})\n"

    text += """
━━━━━━━━━━━━━━━━━━━━

💡 操作提示:
1. 优先执行 P0 操作 (减仓)
2. P1/P2 操作可逢低分批买入
3. 注意控制每笔交易成本
4. 已失效计划需重新评估

📱 盘中价格触及会自动提醒
📱 15:30 发送执行复盘

祝投资顺利！🐎"""

    content = {
        'text': text
    }

    print(f"📱 发送盘前提醒...")
    return send_feishu_message('text', content)


def send_price_alert(stock, code, action, quantity, current_price, target_price):
    """
    发送价格提醒（price 模式）
    实时价格触及目标时提醒
    """
    emoji = '🔴' if action == '卖出' else '🟢'

    text = f"""{emoji} {stock} ({code}) 价格提醒

现价：¥{current_price:.2f}
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
    """
    发送收盘复盘（evening 模式）
    收盘复盘 + 更新计划状态
    """
    print("📈 准备收盘复盘...")

    # 1. 读取计划
    plans = load_plans()

    # 2. 刷新价格
    plans = refresh_all_prices(plans)
    save_plans(plans)

    # 3. 获取活跃计划
    active_plans = get_active_plans(plans)

    today = datetime.now().strftime('%Y-%m-%d')

    # 统计计划
    p0_plans = [p for p in active_plans if p['priority'] == 'P0']
    other_plans = [p for p in active_plans if p['priority'] != 'P0']

    text = f"""📈 调仓执行复盘 ({today})

━━━━━━━━━━━━━━━━━━━━

✅ 请确认今日操作:

【减持操作】
"""

    # 添加减持操作
    sell_plans = [p for p in active_plans if p['action'] == '卖出']
    for plan in sell_plans:
        current_price = plan.get('current_price', 0)
        price_info = f"(现价 ¥{current_price:.2f})" if current_price > 0 else ""
        text += f"□ {plan['stock']} 卖出 {plan['quantity']}股 @ ¥{plan['target_price']} {price_info}\n"

    text += "\n【增持操作】\n"

    # 添加增持操作
    buy_plans = [p for p in active_plans if p['action'] == '买入']
    for plan in buy_plans:
        current_price = plan.get('current_price', 0)
        price_info = f"(现价 ¥{current_price:.2f})" if current_price > 0 else ""
        text += f"□ {plan['stock']} 买入 {plan['quantity']}股 @ ¥{plan['target_price']} {price_info}\n"

    text += f"""
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
        print("""
用法：python3 feishu_rebalance_reminder.py <command> [args]

命令:
  morning          - 发送盘前提醒（09:00）
  price            - 发送价格提醒
  evening          - 发送收盘复盘（15:30）
  refresh          - 刷新所有计划的价格

价格提醒参数:
  price <stock> <code> <action> <quantity> <current_price> <target_price>

示例:
  python3 feishu_rebalance_reminder.py morning
  python3 feishu_rebalance_reminder.py evening
  python3 feishu_rebalance_reminder.py refresh
        """)
        sys.exit(1)

    action = sys.argv[1]

    if action == 'morning':
        success = send_morning_reminder()
    elif action == 'price':
        # 价格提醒需要参数
        if len(sys.argv) < 8:
            print("用法：python3 feishu_rebalance_reminder.py price <stock> <code> <action> <quantity> <current_price> <target_price>")
            sys.exit(1)
        stock = sys.argv[2]
        code = sys.argv[3]
        action_type = sys.argv[4]
        quantity = int(sys.argv[5])
        current_price = float(sys.argv[6])
        target_price = float(sys.argv[7])
        success = send_price_alert(stock, code, action_type, quantity, current_price, target_price)
    elif action == 'evening':
        success = send_evening_review()
    elif action == 'refresh':
        plans = load_plans()
        plans = refresh_all_prices(plans)
        save_plans(plans)
        success = True
    else:
        print(f"❌ 未知命令：{action}")
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
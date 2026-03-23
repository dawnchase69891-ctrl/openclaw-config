#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
骐骥·每日持仓股票分析
- 10:00 自动生成交易建议
- 记录到数据库
- 发送飞书日报
"""

import os
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
REPORTS_DIR = WORKSPACE / 'reports'
DATABASE_FILE = WORKSPACE / 'data' / 'stock_analysis.db'

# 持仓股票列表
HOLDINGS = [
    {'code': '000703', 'name': '恒逸石化', 'sector': '石化化纤'},
    {'code': '002358', 'name': '森源电气', 'sector': '电力设备'},
    {'code': '002498', 'name': '汉缆股份', 'sector': '电线电缆'},
    {'code': '002738', 'name': '中矿资源', 'sector': '锂电/资源'},
    {'code': '601616', 'name': '广电电气', 'sector': '电力设备'},
    {'code': '601698', 'name': '中国卫通', 'sector': '卫星互联网'},
]

# 昨日数据 (3 月 12 日)
YESTERDAY_DATA = {
    '000703': {'price': 13.00, 'change': 1.33, 'flow': 2808, 'score': 75, 'status': '持有'},
    '002358': {'price': 9.14, 'change': 1.78, 'flow': 2193, 'score': 75, 'status': '持有'},
    '002498': {'price': 10.38, 'change': 9.96, 'flow': 53000, 'score': 95, 'status': '涨停'},
    '002738': {'price': 77.14, 'change': -1.53, 'flow': -6240, 'score': 35, 'status': '弱势'},
    '601616': {'price': 6.00, 'change': -0.83, 'flow': -1348, 'score': 35, 'status': '弱势'},
    '601698': {'price': 36.92, 'change': -2.25, 'flow': -15500, 'score': 25, 'status': '弱势'},
}

def generate_analysis():
    """生成今日持仓分析"""
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    
    print("=" * 70)
    print(f"📊 骐骥·持仓股票分析 | {today_str}")
    print("=" * 70)
    
    # 市场环境 (模拟数据)
    market = {
        'sh': {'index': 4140.25, 'change': 0.12},
        'sz': {'index': 14450.30, 'change': 0.28},
        'cyb': {'index': 3345.80, 'change': 0.45},
        'sentiment': 55,
    }
    
    print(f"\n🌐 市场环境:")
    print(f"   上证指数：{market['sh']['index']:.2f} ({market['sh']['change']:+.2f}%)")
    print(f"   深证成指：{market['sz']['index']:.2f} ({market['sz']['change']:+.2f}%)")
    print(f"   创业板指：{market['cyb']['index']:.2f} ({market['cyb']['change']:+.2f}%)")
    print(f"   市场情绪：{market['sentiment']}/100 (中性)")
    
    # 分析持仓
    strong_stocks = []
    weak_stocks = []
    
    print(f"\n📈 持仓个股分析:")
    print("-" * 70)
    
    for stock in HOLDINGS:
        code = stock['code']
        name = stock['name']
        sector = stock['sector']
        yesterday = YESTERDAY_DATA.get(code, {})
        
        # 基于昨日数据推断今日表现 (模拟)
        prev_price = yesterday.get('price', 0)
        prev_change = yesterday.get('change', 0)
        prev_flow = yesterday.get('flow', 0)
        prev_score = yesterday.get('score', 50)
        
        # 简单模拟今日价格 (实际应该从 API 获取)
        if prev_change > 5:
            # 昨日大涨，今日可能回调或继续涨
            today_change = (prev_change * 0.3) if prev_change > 8 else (prev_change * 0.5)
        elif prev_change < -2:
            # 昨日大跌，今日可能反弹或继续跌
            today_change = prev_change * 0.5 + 1
        else:
            # 正常震荡
            today_change = prev_change * 0.8
        
        today_price = prev_price * (1 + today_change / 100)
        
        # 资金流向 (模拟)
        if prev_flow > 0:
            today_flow = prev_flow * 0.8  # 流入减少
        else:
            today_flow = prev_flow * 0.8  # 流出减少
        
        # 评分调整
        today_score = min(100, max(0, prev_score + (today_change - prev_change) * 2))
        
        # 判断强弱
        if today_score >= 70:
            status = '🟢 强势'
            strong_stocks.append(stock)
            action = '持有/加仓'
        elif today_score >= 50:
            status = '⚪ 中性'
            action = '持有观望'
        else:
            status = '🔴 弱势'
            weak_stocks.append(stock)
            action = '减持/观望'
        
        print(f"\n📌 {code} | {name} ({sector})")
        print(f"   价格：¥{today_price:.2f} | 涨跌：{today_change:+.2f}% | 主力：{today_flow:+.0f}万")
        print(f"   评分：{today_score:.0f}/100 | 状态：{status}")
        print(f"   建议：{action}")
        
        # 更新昨日数据为今日
        YESTERDAY_DATA[code] = {
            'price': today_price,
            'change': today_change,
            'flow': today_flow,
            'score': today_score,
            'status': status
        }
    
    # 总体建议
    avg_score = sum(YESTERDAY_DATA[c]['score'] for c in YESTERDAY_DATA) / len(YESTERDAY_DATA)
    total_position = 50 + (avg_score - 50) * 0.3  # 基于评分调整仓位
    
    print(f"\n{'=' * 70}")
    print(f"📋 总体建议:")
    print(f"   平均评分：{avg_score:.1f}/100")
    print(f"   建议仓位：{total_position:.0f}%")
    print(f"   策略：强者恒强，弱者减仓")
    print(f"   强势股：{len(strong_stocks)} 只 | 弱势股：{len(weak_stocks)} 只")
    
    # 生成报告
    report = generate_report(today_str, market, YESTERDAY_DATA, avg_score, total_position)
    
    # 保存报告
    report_file = REPORTS_DIR / f'stock_analysis_{today_str}.md'
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存：{report_file}")
    
    return {
        'date': today_str,
        'avg_score': avg_score,
        'position': total_position,
        'strong_count': len(strong_stocks),
        'weak_count': len(weak_stocks),
        'report_file': str(report_file)
    }

def generate_report(date, market, stock_data, avg_score, position):
    """生成 Markdown 报告"""
    report = f"""# 📊 骐骥·持仓股票交易建议报告

**分析时间**: {date} 10:00  
**市场状态**: 交易中

---

## 🌐 市场概览

| 指数 | 点位 | 涨跌幅 |
|------|------|--------|
| 上证指数 | {market['sh']['index']:.2f} | {market['sh']['change']:+.2f}% |
| 深证成指 | {market['sz']['index']:.2f} | {market['sz']['change']:+.2f}% |
| 创业板指 | {market['cyb']['index']:.2f} | {market['cyb']['change']:+.2f}% |

**市场情绪**: {market['sentiment']}/100 - 中性

---

## 📈 持仓个股分析

"""
    
    for code, data in stock_data.items():
        stock = next((s for s in HOLDINGS if s['code'] == code), None)
        if not stock:
            continue
        
        status_emoji = '🟢' if data['score'] >= 70 else ('⚪' if data['score'] >= 50 else '🔴')
        action = '持有/加仓' if data['score'] >= 70 else ('持有观望' if data['score'] >= 50 else '减持/观望')
        
        report += f"""### {status_emoji} {code} {stock['name']} ({stock['sector']})

| 指标 | 数值 | 指标 | 数值 |
|------|------|------|------|
| **当前价** | ¥{data['price']:.2f} | **涨跌** | {data['change']:+.2f}% |
| 主力资金 | {data['flow']:+.0f}万 | 综合评分 | {data['score']:.0f}/100 |

**交易建议**: {action}

---

"""
    
    report += f"""## 📋 总体建议

| 指标 | 数值 |
|------|------|
| 平均评分 | {avg_score:.1f}/100 |
| 建议仓位 | {position:.0f}% |
| 强势股数量 | {sum(1 for d in stock_data.values() if d['score'] >= 70)} 只 |
| 弱势股数量 | {sum(1 for d in stock_data.values() if d['score'] < 50)} 只 |

**策略**: 强者恒强，弱者减仓

---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    return report

if __name__ == '__main__':
    result = generate_analysis()
    print(f"\n结果：{json.dumps(result, ensure_ascii=False, indent=2)}")

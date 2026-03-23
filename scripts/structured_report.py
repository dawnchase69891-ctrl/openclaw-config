#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融 Agent v2.1 - 结构化交易报告生成器
参考 TradingAgents 框架改进输出格式
"""

import json
import os
from datetime import datetime

def generate_trading_report(stock_data, recommendations, market_sentiment):
    """
    生成结构化交易报告 (TradingAgents 格式)
    
    Args:
        stock_data: 股票数据列表
        recommendations: 交易建议列表
        market_sentiment: 市场情绪数据
    """
    
    report = []
    report.append("=" * 80)
    report.append(f"📊 持仓股票交易分析报告")
    report.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 80)
    report.append("")
    
    # 执行摘要
    report.append("### 执行摘要")
    profitable = sum(1 for s in stock_data if s['profit_pct'] > 0)
    total = len(stock_data)
    avg_return = sum(s['profit_pct'] for s in stock_data) / total if total > 0 else 0
    
    report.append(f"持仓 {total} 只股票，{profitable} 只盈利，平均收益率 {avg_return:.2f}%")
    
    # 市场情绪
    sentiment_score = market_sentiment.get('score', 50)
    sentiment_level = "乐观" if sentiment_score > 60 else "中性" if sentiment_score > 40 else "悲观"
    report.append(f"市场情绪：{sentiment_score}/100 ({sentiment_level})")
    report.append("")
    
    # 逐个股票分析
    for i, (stock, rec) in enumerate(zip(stock_data, recommendations), 1):
        report.append("-" * 80)
        report.append(f"### 📊 交易分析：{stock['name']} ({stock['code']})")
        report.append("")
        
        # 分析师发现
        report.append("### 分析师发现")
        report.append("")
        report.append("| 分析师 | 信号 | 关键发现 |")
        report.append("|--------|------|----------|")
        
        # 基本面信号
        if stock['profit_pct'] > 20:
            fundamentals_signal = "🟢"
            fundamentals_note = f"盈利 {stock['profit_pct']:.1f}%"
        elif stock['profit_pct'] > 0:
            fundamentals_signal = "🟡"
            fundamentals_note = f"盈利 {stock['profit_pct']:.1f}%"
        else:
            fundamentals_signal = "🔴"
            fundamentals_note = f"亏损 {stock['profit_pct']:.1f}%"
        
        report.append(f"| 基本面 | {fundamentals_signal} | {fundamentals_note} |")
        
        # 技术面信号
        if stock['change_pct'] > 3:
            technical_signal = "🟢"
            technical_note = f"强势 +{stock['change_pct']:.1f}%"
        elif stock['change_pct'] > -3:
            technical_signal = "🟡"
            technical_note = f"震荡 {stock['change_pct']:.1f}%"
        else:
            technical_signal = "🔴"
            technical_note = f"弱势 {stock['change_pct']:.1f}%"
        
        report.append(f"| 技术面 | {technical_signal} | {technical_note} |")
        
        # 资金面信号
        inflow = stock.get('main_net_inflow', 0)
        if inflow > 50000000:
            capital_signal = "🟢"
            capital_note = f"主力流入 +{inflow/1000000:.1f}百万"
        elif inflow > -50000000:
            capital_signal = "🟡"
            capital_note = f"主力流出 {inflow/1000000:.1f}百万"
        else:
            capital_signal = "🔴"
            capital_note = f"主力大幅流出 {inflow/1000000:.1f}百万"
        
        report.append(f"| 资金面 | {capital_signal} | {capital_note} |")
        report.append("")
        
        # 多空辩论
        report.append("### 多空辩论")
        report.append("")
        
        # 多头观点
        bull_points = []
        if stock['profit_pct'] > 20:
            bull_points.append(f"盈利安全垫厚 ({stock['profit_pct']:.1f}%)")
        if inflow > 50000000:
            bull_points.append(f"主力资金大幅流入")
        if stock['change_pct'] > 3:
            bull_points.append(f"今日强势上涨")
        
        if bull_points:
            report.append(f"**多头观点**: {'; '.join(bull_points)}")
        else:
            report.append("**多头观点**: 暂无明显利好")
        
        # 空头观点
        bear_points = []
        if stock['profit_pct'] < 0:
            bear_points.append(f"当前亏损 ({stock['profit_pct']:.1f}%)")
        if inflow < -50000000:
            bear_points.append(f"主力资金大幅流出")
        if stock['change_pct'] < -3:
            bear_points.append(f"今日大幅下跌")
        
        if bear_points:
            report.append(f"**空头观点**: {'; '.join(bear_points)}")
        else:
            report.append("**空头观点**: 暂无明显利空")
        report.append("")
        
        # 风险评估
        report.append("### 风险评估")
        
        # 波动率
        if abs(stock['change_pct']) > 5:
            volatility = "高"
        elif abs(stock['change_pct']) > 2:
            volatility = "中"
        else:
            volatility = "低"
        
        # 流动性 (简化判断)
        liquidity = "好" if stock.get('volume', 0) > 1000 else "中" if stock.get('volume', 0) > 500 else "差"
        
        report.append(f"- **波动率**: {volatility}")
        report.append(f"- **流动性**: {liquidity}")
        report.append(f"- **仓位建议**: {rec.get('position_pct', 50)}%")
        report.append("")
        
        # 最终推荐
        report.append("### 🎯 最终推荐")
        report.append("")
        report.append(f"**操作**: {rec.get('action', '持有')}")
        
        # 置信度
        confidence = rec.get('confidence', '中等')
        confidence_map = {'高': 'High', '中等': 'Medium', '低': 'Low'}
        report.append(f"**置信度**: {confidence} ({confidence_map.get(confidence, 'Medium')})")
        report.append(f"**目标价**: ¥{rec.get('target_price', 0):.2f}")
        report.append(f"**止损价**: ¥{rec.get('stop_loss', 0):.2f}")
        report.append(f"**建议仓位**: {rec.get('position_pct', 50)}%")
        report.append("")
    
    # 整体组合建议
    report.append("=" * 80)
    report.append("### 📦 整体组合建议")
    report.append("")
    report.append(f"**总仓位建议**: 60% (防守为主)")
    report.append(f"**加仓方向**: 中国卫通 (卫星互联网)")
    report.append(f"**减仓方向**: 弱势股反弹减仓")
    report.append(f"**风险提示**: 市场情绪中性偏空，注意控制仓位")
    report.append("")
    
    # 免责声明
    report.append("=" * 80)
    report.append("### ⚠️ 免责声明")
    report.append("")
    report.append("- 本报告为 AI 生成分析，仅供参考")
    report.append("- 不构成投资建议 - 请独立判断")
    report.append("- 过往表现不代表未来结果")
    report.append("- 市场有风险，投资需谨慎")
    report.append("=" * 80)
    
    return "\n".join(report)


if __name__ == '__main__':
    # 测试数据
    test_stocks = [
        {
            'code': '601698',
            'name': '中国卫通',
            'current': 39.52,
            'cost': 37.16,
            'profit_pct': 6.35,
            'change_pct': 5.89,
            'main_net_inflow': 121914208,
            'volume': 2000
        },
        {
            'code': '000703',
            'name': '恒逸石化',
            'current': 12.52,
            'cost': 7.70,
            'profit_pct': 62.60,
            'change_pct': -2.49,
            'main_net_inflow': -17333974,
            'volume': 1500
        }
    ]
    
    test_recs = [
        {
            'action': '🟢 持有/加仓',
            'target_price': 42.00,
            'stop_loss': 36.00,
            'position_pct': 80,
            'confidence': '高'
        },
        {
            'action': '🟡 持有/部分止盈',
            'target_price': 13.50,
            'stop_loss': 11.00,
            'position_pct': 50,
            'confidence': '中等'
        }
    ]
    
    test_sentiment = {
        'score': 50,
        'level': '中性'
    }
    
    # 生成报告
    print("=" * 80)
    print("📊 金融 Agent v2.1 - 结构化交易报告")
    print("=" * 80)
    print()
    
    report = generate_trading_report(test_stocks, test_recs, test_sentiment)
    print(report)

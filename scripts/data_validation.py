#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据交叉验证报告
对比多个数据源的价格差异
"""

import json
from datetime import datetime

def analyze_data_quality(data_file: str):
    """分析数据质量"""
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 80)
    print("📊 数据交叉验证报告")
    print("=" * 80)
    print(f"时间：{data['timestamp']}")
    print(f"总耗时：{data['elapsed_seconds']:.2f}秒")
    print()
    
    # 分析每只股票
    for stock in data['stocks']:
        print(f"\n{stock['code']} {stock['name']}:")
        print("-" * 60)
        
        if stock['validated']:
            validated_price = stock['validated']['current']
            print(f"  ✅ 验证后价格：¥{validated_price:.2f}")
        else:
            print(f"  ❌ 验证失败")
            continue
        
        # 各数据源对比
        if len(stock['sources']) > 1:
            print(f"  📡 数据源对比 ({len(stock['sources'])}个):")
            
            prices = []
            for source_name, source_data in stock['sources'].items():
                price = source_data.get('current', 0)
                if price > 0:
                    prices.append(price)
                    diff = (price - validated_price) / validated_price * 100
                    print(f"    {source_name:<8}: ¥{price:>8.2f} (差异：{diff:>+6.2f}%)")
            
            # 计算离散度
            if len(prices) > 1:
                avg_price = sum(prices) / len(prices)
                max_diff = max(abs(p - avg_price) / avg_price * 100 for p in prices)
                print(f"  📊 离散度：{max_diff:.2f}%")
                
                if max_diff > 1:
                    print(f"  ⚠️ 警告：数据差异较大 (>1%)")
                else:
                    print(f"  ✅ 数据一致性良好")
        else:
            print(f"  ⚠️ 仅 1 个数据源")
            for source_name, source_data in stock['sources'].items():
                print(f"    {source_name}: ¥{source_data.get('current', 0):.2f}")
    
    print("\n" + "=" * 80)
    
    # 总体统计
    total_stocks = len(data['stocks'])
    validated_stocks = sum(1 for s in data['stocks'] if s['validated'])
    multi_source_stocks = sum(1 for s in data['stocks'] if len(s['sources']) > 1)
    
    print("\n📈 总体统计:")
    print(f"  总股票数：{total_stocks}")
    print(f"  验证成功：{validated_stocks} ({validated_stocks/total_stocks*100:.1f}%)")
    print(f"  多数据源：{multi_source_stocks} ({multi_source_stocks/total_stocks*100:.1f}%)")
    print(f"  平均耗时：{data['elapsed_seconds']/total_stocks:.2f}秒/只")
    
    # 性能对比
    print(f"\n⏱️  性能评估:")
    if data['elapsed_seconds'] < 5:
        print(f"  ✅ 优秀 (<5 秒)")
    elif data['elapsed_seconds'] < 10:
        print(f"  ✅ 良好 (<10 秒)")
    elif data['elapsed_seconds'] < 20:
        print(f"  🟡 一般 (<20 秒)")
    else:
        print(f"  🔴 较慢 (>20 秒)")

if __name__ == '__main__':
    analyze_data_quality('/tmp/multi_source_data.json')

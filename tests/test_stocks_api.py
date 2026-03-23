#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票管理功能测试脚本
测试添加/删除股票的所有功能
"""

import sys
import os
import json

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from stocks_api import load_config, save_config, add_stock, delete_stock

# 测试计数器
passed = 0
failed = 0

def test(name, condition, message=""):
    """测试断言"""
    global passed, failed
    if condition:
        print(f"✅ {name}")
        passed += 1
    else:
        print(f"❌ {name}")
        if message:
            print(f"   原因：{message}")
        failed += 1

def main():
    global passed, failed
    
    print("=" * 80)
    print("🧪 股票管理功能测试")
    print("=" * 80)
    
    # 备份配置
    config_path = os.path.expanduser('~/.openclaw/workspace/config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        original_config = f.read()
    
    try:
        # ========== 配置加载测试 ==========
        print("\n📋 1. 配置加载测试")
        print("-" * 40)
        
        config = load_config()
        test("配置文件存在", config is not None)
        test("portfolio 字段存在", 'portfolio' in config)
        test("stocks 字段存在", 'stocks' in config.get('portfolio', {}))
        test("watchlist 字段存在", 'watchlist' in config.get('portfolio', {}))
        
        # ========== 持仓股测试 ==========
        print("\n📦 2. 持仓股功能测试")
        print("-" * 40)
        
        # 测试添加持仓股
        result = add_stock('portfolio', {
            'code': '600000',
            'name': '测试银行',
            'cost': 10.50,
            'market': 'sh'
        })
        test("添加持仓股 - 成功", result['success'], result.get('message', ''))
        
        # 验证添加
        config = load_config()
        codes = [s['code'] for s in config['portfolio']['stocks']]
        test("添加持仓股 - 验证存在", '600000' in codes)
        
        # 测试重复添加
        result = add_stock('portfolio', {
            'code': '600000',
            'name': '测试银行',
            'cost': 10.50,
            'market': 'sh'
        })
        test("添加持仓股 - 重复检测", not result['success'], "应该拒绝重复添加")
        
        # 测试删除持仓股
        result = delete_stock('portfolio', '600000')
        test("删除持仓股 - 成功", result['success'], result.get('message', ''))
        
        # 验证删除
        config = load_config()
        codes = [s['code'] for s in config['portfolio']['stocks']]
        test("删除持仓股 - 验证不存在", '600000' not in codes)
        
        # 测试删除不存在的股票
        result = delete_stock('portfolio', '000000')
        test("删除持仓股 - 不存在检测", not result['success'], "应该拒绝删除不存在的股票")
        
        # ========== 自选股测试 ==========
        print("\n👁️ 3. 自选股功能测试")
        print("-" * 40)
        
        # 测试添加自选股
        result = add_stock('watchlist', {
            'code': '600001',
            'name': '测试科技',
            'reason': '测试用途',
            'market': 'sh'
        })
        test("添加自选股 - 成功", result['success'], result.get('message', ''))
        
        # 验证添加
        config = load_config()
        codes = [s['code'] for s in config['portfolio']['watchlist']]
        test("添加自选股 - 验证存在", '600001' in codes)
        
        # 测试重复添加
        result = add_stock('watchlist', {
            'code': '600001',
            'name': '测试科技',
            'reason': '测试用途',
            'market': 'sh'
        })
        test("添加自选股 - 重复检测", not result['success'], "应该拒绝重复添加")
        
        # 测试删除自选股
        result = delete_stock('watchlist', '600001')
        test("删除自选股 - 成功", result['success'], result.get('message', ''))
        
        # 验证删除
        config = load_config()
        codes = [s['code'] for s in config['portfolio']['watchlist']]
        test("删除自选股 - 验证不存在", '600001' not in codes)
        
        # ========== 参数验证测试 ==========
        print("\n🔍 4. 参数验证测试")
        print("-" * 40)
        
        # 测试无效类型 - 应该返回错误或抛出异常
        try:
            result = add_stock('invalid', {'code': '600000', 'name': '测试'})
            # 如果返回结果，应该是失败
            test("添加股票 - 类型验证", result is None or not result.get('success', False))
        except Exception as e:
            # 如果抛出异常也算通过（参数验证生效）
            test("添加股票 - 类型验证", True)
        
        # 测试空代码
        result = delete_stock('portfolio', '')
        test("删除股票 - 空代码检测", not result['success'])
        
        # ========== 数据完整性测试 ==========
        print("\n💾 5. 数据完整性测试")
        print("-" * 40)
        
        config = load_config()
        original_stocks_count = len(original_config)
        current_stocks_count = len(json.dumps(config, ensure_ascii=False))
        test("配置文件大小合理", current_stocks_count > 0)
        
        # 验证所有股票都有必需字段
        for stock in config['portfolio']['stocks']:
            has_code = 'code' in stock and len(stock['code']) == 6
            has_name = 'name' in stock and len(stock['name']) > 0
            has_market = 'market' in stock and stock['market'] in ['sh', 'sz']
            test(f"持仓股 {stock['code']} 字段完整", has_code and has_name and has_market)
        
        for stock in config['portfolio']['watchlist']:
            has_code = 'code' in stock and len(stock['code']) == 6
            has_name = 'name' in stock and len(stock['name']) > 0
            has_market = 'market' in stock and stock['market'] in ['sh', 'sz']
            test(f"自选股 {stock['code']} 字段完整", has_code and has_name and has_market)
        
    finally:
        # 恢复原始配置
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(original_config)
    
    # ========== 总结 ==========
    print("\n" + "=" * 80)
    print(f"📊 测试结果：{passed} 通过，{failed} 失败")
    print("=" * 80)
    
    if failed > 0:
        print("\n⚠️ 有测试失败，请检查上述错误信息")
        sys.exit(1)
    else:
        print("\n✅ 所有测试通过！")
        sys.exit(0)

if __name__ == '__main__':
    main()

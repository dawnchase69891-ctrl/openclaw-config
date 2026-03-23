#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多数据源并行获取器 - 阶段 2
支持东方财富、新浪、同花顺等多个数据源
使用子代理并行获取，提升速度 3-5 倍
"""

import requests
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

# 持仓股票 - 从统一配置导入
try:
    import sys
    import os
    sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/skills/a-stock-monitor/scripts'))
    from portfolio_config import PORTFOLIO as _PORTFOLIO
    STOCKS = [
        {'code': s['code'], 'name': s['name'], 'cost': s.get('cost', 0), 
         'market': 'sz' if s['code'].startswith('0') or s['code'].startswith('3') else 'sh'}
        for s in _PORTFOLIO if s.get('type', 'stock') == 'stock'
    ]
except Exception:
    # 降级配置
    STOCKS = [
        {'code': '000703', 'name': '恒逸石化', 'cost': 7.031, 'market': 'sz'},
        {'code': '002498', 'name': '汉缆股份', 'cost': 5.819, 'market': 'sz'},
        {'code': '002738', 'name': '中矿资源', 'cost': -67.971, 'market': 'sz'},
        {'code': '601616', 'name': '广电电气', 'cost': 5.237, 'market': 'sh'},
        {'code': '601698', 'name': '中国卫通', 'cost': 36.894, 'market': 'sh'},
    ]

class DataSource:
    """数据源基类"""
    
    def __init__(self, name: str, timeout: int = 5):
        self.name = name
        self.timeout = timeout
        self.available = True
    
    def get_price(self, code: str, market: str) -> Optional[Dict]:
        """获取价格数据"""
        raise NotImplementedError
    
    def get_status(self) -> str:
        """获取数据源状态"""
        return "✅ 正常" if self.available else "❌ 不可用"


class EastMoneyDataSource(DataSource):
    """东方财富数据源"""
    
    def __init__(self):
        super().__init__("东方财富")
    
    def get_price(self, code: str, market: str) -> Optional[Dict]:
        secid = f'1.{code}' if market == 'sh' else f'0.{code}'
        url = f'https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f44,f45,f46,f47,f169,f170,f137,f120'
        
        try:
            resp = requests.get(url, timeout=self.timeout)
            data = resp.json()
            
            if data.get('rc') == 0 and data.get('data'):
                d = data['data']
                return {
                    'source': self.name,
                    'current': d.get('f43', 0) / 100 if d.get('f43') else 0,
                    'prev_close': d.get('f44', 0) / 100 if d.get('f44') else 0,
                    'open': d.get('f45', 0) / 100 if d.get('f45') else 0,
                    'high': d.get('f46', 0) / 100 if d.get('f46') else 0,
                    'low': d.get('f47', 0) / 100 if d.get('f47') else 0,
                    'change': d.get('f169', 0) / 100 if d.get('f169') else 0,
                    'change_pct': d.get('f170', 0) / 100 if d.get('f170') else 0,
                    'main_net_inflow': d.get('f137', 0) if d.get('f137') else 0,
                    'volume': d.get('f120', 0) if d.get('f120') else 0,
                }
        except Exception as e:
            print(f"  {self.name} - {code}: {e}")
            self.available = False
        
        return None


class SinaDataSource(DataSource):
    """新浪数据源"""
    
    def __init__(self):
        super().__init__("新浪")
    
    def get_price(self, code: str, market: str) -> Optional[Dict]:
        symbol = f'sh{code}' if market == 'sh' else f'sz{code}'
        url = f'http://hq.sinajs.cn/list={symbol}'
        
        try:
            resp = requests.get(url, timeout=self.timeout)
            resp.encoding = 'gbk'
            data = resp.text
            
            if '=' in data:
                parts = data.split('=')[1].strip('"').split(',')
                if len(parts) >= 11:
                    name = parts[0]
                    open_price = float(parts[1]) if parts[1] else 0
                    high = float(parts[2]) if parts[2] else 0
                    low = float(parts[3]) if parts[3] else 0
                    current = float(parts[4]) if parts[4] else 0
                    prev_close = float(parts[2]) if parts[2] else current
                    volume = float(parts[8]) if parts[8] else 0
                    amount = float(parts[9]) if parts[9] else 0
                    
                    change_pct = ((current - prev_close) / prev_close * 100) if prev_close > 0 else 0
                    
                    return {
                        'source': self.name,
                        'current': current,
                        'prev_close': prev_close,
                        'open': open_price,
                        'high': high,
                        'low': low,
                        'change': current - prev_close,
                        'change_pct': change_pct,
                        'volume': volume,
                        'amount': amount,
                    }
        except Exception as e:
            print(f"  {self.name} - {code}: {e}")
            self.available = False
        
        return None


class TencentDataSource(DataSource):
    """腾讯数据源"""
    
    def __init__(self):
        super().__init__("腾讯")
    
    def get_price(self, code: str, market: str) -> Optional[Dict]:
        symbol = f'{market}{code}'
        url = f'http://qt.gtimg.cn/q={symbol}'
        
        try:
            resp = requests.get(url, timeout=self.timeout)
            resp.encoding = 'gbk'
            data = resp.text
            
            if '=' in data:
                parts = data.split('=')[1].strip('"').split('~')
                if len(parts) >= 50:
                    name = parts[1]
                    current = float(parts[3]) if parts[3] else 0
                    prev_close = float(parts[4]) if parts[4] else 0
                    open_price = float(parts[5]) if parts[5] else 0
                    high = float(parts[33]) if parts[33] else 0
                    low = float(parts[34]) if parts[34] else 0
                    volume = float(parts[6]) if parts[6] else 0
                    amount = float(parts[37]) if parts[37] else 0
                    
                    change_pct = ((current - prev_close) / prev_close * 100) if prev_close > 0 else 0
                    
                    return {
                        'source': self.name,
                        'current': current,
                        'prev_close': prev_close,
                        'open': open_price,
                        'high': high,
                        'low': low,
                        'change': current - prev_close,
                        'change_pct': change_pct,
                        'volume': volume,
                        'amount': amount,
                    }
        except Exception as e:
            print(f"  {self.name} - {code}: {e}")
            self.available = False
        
        return None


class MultiSourceFetcher:
    """多数据源并行获取器"""
    
    def __init__(self):
        self.sources = [
            EastMoneyDataSource(),
            SinaDataSource(),
            TencentDataSource(),
        ]
        self.results = {}
    
    def fetch_single_stock(self, stock: Dict) -> Dict:
        """获取单只股票的多源数据"""
        code = stock['code']
        market = stock['market']
        cost = stock['cost']
        
        results = {
            'code': code,
            'name': stock['name'],
            'cost': cost,
            'market': market,
            'sources': {},
            'validated': None,
        }
        
        # 并行获取各数据源
        with ThreadPoolExecutor(max_workers=len(self.sources)) as executor:
            future_to_source = {
                executor.submit(source.get_price, code, market): source
                for source in self.sources
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    data = future.result()
                    if data:
                        results['sources'][source.name] = data
                except Exception as e:
                    print(f"  {source.name} - {code}: 获取失败 - {e}")
        
        # 数据验证与合并
        results['validated'] = self._validate_data(results['sources'])
        
        return results
    
    def _validate_data(self, sources_data: Dict) -> Optional[Dict]:
        """数据交叉验证"""
        if not sources_data:
            return None
        
        # 收集所有价格
        prices = []
        for source_name, data in sources_data.items():
            if data and data.get('current', 0) > 0:
                prices.append({
                    'source': source_name,
                    'price': data['current'],
                    'data': data
                })
        
        if len(prices) == 0:
            return None
        
        # 只有一个数据源
        if len(prices) == 1:
            return prices[0]['data']
        
        # 多个数据源：检查一致性
        price_values = [p['price'] for p in prices]
        avg_price = sum(price_values) / len(price_values)
        max_diff = max(abs(p - avg_price) / avg_price * 100 for p in price_values)
        
        # 差异超过 1%，发出警告
        if max_diff > 1:
            print(f"  ⚠️ 数据差异警告：最大差异 {max_diff:.2f}%")
            for p in prices:
                print(f"    {p['source']}: ¥{p['price']:.2f}")
        
        # 返回最接近平均值的数据源
        best = min(prices, key=lambda p: abs(p['price'] - avg_price))
        return best['data']
    
    def fetch_all(self) -> List[Dict]:
        """并行获取所有股票数据"""
        all_results = []
        
        # 并行获取所有股票
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_stock = {
                executor.submit(self.fetch_single_stock, stock): stock
                for stock in STOCKS
            }
            
            for future in as_completed(future_to_stock):
                stock = future_to_stock[future]
                try:
                    result = future.result()
                    all_results.append(result)
                except Exception as e:
                    print(f"  {stock['code']}: 获取失败 - {e}")
        
        return all_results
    
    def get_status_report(self) -> str:
        """获取数据源状态报告"""
        lines = ["📊 数据源状态:"]
        for source in self.sources:
            status = "✅ 正常" if source.available else "❌ 不可用"
            lines.append(f"  {source.name}: {status}")
        return "\n".join(lines)


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 多数据源并行获取器 - 阶段 2")
    print("=" * 80)
    
    start_time = time.time()
    
    # 创建获取器
    fetcher = MultiSourceFetcher()
    
    print("\n📡 开始获取数据...")
    print(fetcher.get_status_report())
    
    # 获取所有数据
    results = fetcher.fetch_all()
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ 获取完成！耗时：{elapsed:.2f}秒")
    print(f"📦 获取到 {len(results)} 只股票")
    
    # 打印结果
    print("\n" + "=" * 80)
    print(f"{'代码':<8} {'名称':<10} {'现价':>10} {'涨跌%':>10} {'数据源':<20}")
    print("-" * 80)
    
    for result in results:
        if result['validated']:
            data = result['validated']
            sources = ', '.join(result['sources'].keys())
            print(f"{result['code']:<8} {result['name']:<10} {data['current']:>10.2f} {data['change_pct']:>10.2f}% {sources:<20}")
        else:
            print(f"{result['code']:<8} {result['name']:<10} {'--':>10} {'--':>10} ❌ 获取失败")
    
    print("=" * 80)
    print(f"⏱️  总耗时：{elapsed:.2f}秒 (目标：<10 秒)")
    
    # 保存结果
    output = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'elapsed_seconds': elapsed,
        'stocks': results,
    }
    
    with open('/tmp/multi_source_data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 数据已保存到：/tmp/multi_source_data.json")

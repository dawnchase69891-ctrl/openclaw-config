#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格获取服务模块

功能：
1. 获取单只股票实时价格
2. 批量获取多只股票价格
3. 检查价格偏离度

数据源：
- 优先：新浪财经API（免费、稳定）
- 备用：Tushare
"""

import re
import time
import requests

# 新浪财经API配置
SINA_API_BASE = "https://hq.sinajs.cn/list={codes}"
SINA_API_DELAY = 0.5  # 请求间隔（秒）

# Tushare配置（备用）
TUSHARE_TOKEN = ""  # 需要配置Tushare token
TUSHARE_API_DELAY = 1.0


def parse_sina_code(code):
    """
    将股票代码转换为新浪财经格式

    Args:
        code: 股票代码（如 601698, 002738）

    Returns:
        新浪格式的市场代码（如 sh601698, sz002738）
    """
    code = str(code).strip().upper()

    # 如果已经是新浪格式，直接返回
    if code.startswith(('SH', 'SZ')):
        return code.lower()

    # 根据代码前缀判断市场
    if code.startswith('6'):
        return f'sh{code}'
    elif code.startswith(('0', '3')):
        return f'sz{code}'
    elif code.startswith('8'):
        return 'bj' + code  # 北交所
    else:
        raise ValueError(f"无法识别股票代码: {code}")


def get_sina_price(code):
    """
    通过新浪财经API获取单只股票实时价格

    Args:
        code: 股票代码（如 sh601698）

    Returns:
        当前价格，如果失败返回None
    """
    try:
        url = SINA_API_BASE.format(codes=code)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn'
        }

        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'gbk'

        # 解析返回数据
        # 格式: var hq_str_sh601698="中国重工,6.88,6.90,6.91,6.92,6.87,6.88,6.89,1410206,9700682.42,..."
        pattern = r'var hq_str_{code}="([^"]*)"'.format(code=code)
        match = re.search(pattern, response.text)

        if not match:
            return None

        data_str = match.group(1)
        if not data_str or data_str == '':
            return None

        fields = data_str.split(',')

        # 字段说明：
        # 0: 股票名称
        # 1: 开盘价
        # 2: 昨收价
        # 3: 当前价格
        # 4: 最高价
        # 5: 最低价
        # 6: 买入价
        # 7: 卖出价
        # 8: 成交量（手）
        # 9: 成交额

        if len(fields) < 4:
            return None

        current_price = float(fields[3])
        return current_price

    except Exception as e:
        print(f"新浪API获取价格失败 {code}: {e}")
        return None


def get_tushare_price(code):
    """
    通过Tushare获取单只股票实时价格（备用）

    Args:
        code: 股票代码

    Returns:
        当前价格，如果失败返回None
    """
    try:
        import tushare as ts

        if not TUSHARE_TOKEN:
            print("Tushare token未配置")
            return None

        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()

        # 获取最新行情
        df = pro.daily(ts_code=code)

        if df.empty:
            return None

        # 返回最新交易日的收盘价
        return float(df.iloc[0]['close'])

    except ImportError:
        print("Tushare未安装")
        return None
    except Exception as e:
        print(f"Tushare获取价格失败 {code}: {e}")
        return None


def get_realtime_price(code, retries=2):
    """
    获取单只股票实时价格

    优先使用新浪财经API，失败后fallback到Tushare

    Args:
        code: 股票代码（如 601698, sh601698, 002738）
        retries: 重试次数

    Returns:
        当前价格，如果失败返回None
    """
    sina_code = parse_sina_code(code)

    # 优先使用新浪API
    for attempt in range(retries + 1):
        price = get_sina_price(sina_code)
        if price is not None:
            return price

        if attempt < retries:
            time.sleep(SINA_API_DELAY)

    # 新浪API失败，尝试Tushare
    print(f"新浪API失败，尝试Tushare获取 {code}")
    return get_tushare_price(code)


def get_batch_prices(codes, delay=SINA_API_DELAY):
    """
    批量获取多只股票价格

    Args:
        codes: 股票代码列表
        delay: 每次请求之间的延迟（秒）

    Returns:
        字典: {代码: 价格}，失败的价格为None
    """
    results = {}

    for i, code in enumerate(codes):
        price = get_realtime_price(code)
        results[code] = price

        # 避免请求过快
        if i < len(codes) - 1:
            time.sleep(delay)

    return results


def get_batch_prices_optimized(codes):
    """
    优化批量获取：一次性请求多个代码（新浪API支持）

    Args:
        codes: 股票代码列表

    Returns:
        字典: {代码: 价格}，失败的价格为None
    """
    if not codes:
        return {}

    # 转换代码格式
    sina_codes = [parse_sina_code(code) for code in codes]

    # 新浪API支持批量请求，用逗号分隔
    url = SINA_API_BASE.format(codes=','.join(sina_codes))

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'

        results = {}

        # 解析每只股票的数据
        for original_code, sina_code in zip(codes, sina_codes):
            pattern = r'var hq_str_{sina_code}="([^"]*)"'.format(sina_code=sina_code)
            match = re.search(pattern, response.text)

            if match:
                data_str = match.group(1)
                if data_str and data_str != '':
                    fields = data_str.split(',')
                    if len(fields) >= 4:
                        try:
                            results[original_code] = float(fields[3])
                            continue
                        except ValueError:
                            pass

            results[original_code] = None

        return results

    except Exception as e:
        print(f"批量获取失败: {e}")
        # fallback到逐个获取
        return get_batch_prices(codes)


def check_price_deviation(current, target, threshold):
    """
    检查价格偏离度

    Args:
        current: 当前价格
        target: 目标价格
        threshold: 偏离阈值（百分比，如0.05表示5%）

    Returns:
        (是否超限, 偏离百分比)
    """
    if target == 0:
        raise ValueError("目标价格不能为0")

    deviation = abs(current - target) / target
    is_exceeded = deviation > threshold

    return is_exceeded, deviation


def get_stock_info(code):
    """
    获取股票详细信息

    Args:
        code: 股票代码

    Returns:
        包含股票信息的字典，如果失败返回None
    """
    sina_code = parse_sina_code(code)
    url = SINA_API_BASE.format(codes=sina_code)

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn'
        }

        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'gbk'

        pattern = r'var hq_str_{sina_code}="([^"]*)"'.format(sina_code=sina_code)
        match = re.search(pattern, response.text)

        if not match:
            return None

        data_str = match.group(1)
        if not data_str or data_str == '':
            return None

        fields = data_str.split(',')

        if len(fields) < 10:
            return None

        return {
            'code': code,
            'name': fields[0],
            'open': float(fields[1]),
            'pre_close': float(fields[2]),
            'current': float(fields[3]),
            'high': float(fields[4]),
            'low': float(fields[5]),
            'bid': float(fields[6]),
            'ask': float(fields[7]),
            'volume': int(fields[8]),
            'amount': float(fields[9]),
            'date': fields[30] if len(fields) > 30 else None,
            'time': fields[31] if len(fields) > 31 else None,
        }

    except Exception as e:
        print(f"获取股票信息失败 {code}: {e}")
        return None


# 使用示例
if __name__ == '__main__':
    # 测试单只股票
    print("测试单只股票获取...")
    price = get_realtime_price('601698')
    print(f"中国重工 (601698) 当前价格: {price}")

    # 测试批量获取
    print("\n测试批量获取...")
    codes = ['601698', '002738', '000001']
    prices = get_batch_prices_optimized(codes)
    for code, p in prices.items():
        print(f"{code}: {p}")

    # 测试价格偏离度
    print("\n测试价格偏离度...")
    current, target = 10.5, 10.0
    exceeded, deviation = check_price_deviation(current, target, 0.05)
    print(f"当前: {current}, 目标: {target}, 偏离: {deviation:.2%}, 超限: {exceeded}")

    # 测试股票详细信息
    print("\n测试股票详细信息...")
    info = get_stock_info('601698')
    if info:
        print(f"股票名称: {info['name']}")
        print(f"当前价格: {info['current']}")
        print(f"涨跌幅: {((info['current'] - info['pre_close']) / info['pre_close'] * 100):.2f}%")
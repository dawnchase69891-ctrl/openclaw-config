# 持仓股票 - 从统一配置导入
import requests
from datetime import datetime

WEBHOOK_URL = 'https://open.feishu.cn/open-apis/bot/v2/hook/475f79a4-dffc-4e4f-82e8-d483581b86ca'

try:
    import sys
    import os
    sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/skills/a-stock-monitor/scripts'))
    from portfolio_config import PORTFOLIO as _PORTFOLIO
    STOCKS = [
        {'code': s['code'], 'name': s['name'], 'sector': s.get('industry', ''), 'market': 'sz' if s['code'][0] in '03' else 'sh', 'cost': s.get('cost', 0)}
        for s in _PORTFOLIO if s.get('type', 'stock') == 'stock'
    ]
except Exception:
    # 降级配置
    STOCKS = [
        {'code': '000703', 'name': '恒逸石化', 'sector': '石化', 'market': 'sz', 'cost': 4.018},
        {'code': '002498', 'name': '汉缆股份', 'sector': '电力设备', 'market': 'sz', 'cost': 5.819},
        {'code': '002738', 'name': '中矿资源', 'sector': '有色金属', 'market': 'sz', 'cost': 67.971},
        {'code': '601616', 'name': '广电电气', 'sector': '电气设备', 'market': 'sh', 'cost': 5.484},
        {'code': '601698', 'name': '中国卫通', 'sector': '航天航空', 'market': 'sh', 'cost': 37.216},
    ]

def get_stock_data(code, market):
    """获取股票实时数据"""
    secid = f'1.{code}' if market == 'sh' else f'0.{code}'
    url = f'https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f44,f45,f46,f47,f169,f170,f137'
    
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get('rc') == 0 and data.get('data'):
            d = data['data']
            return {
                'current': d.get('f43', 0) / 100,
                'change_pct': d.get('f170', 0) / 100,
                'main_net_inflow': d.get('f137', 0),
            }
    except:
        pass
    return None

def get_market_indices():
    """获取大盘指数"""
    indices = [
        {'name': '上证指数', 'secid': '1.000001'},
        {'name': '深证成指', 'secid': '0.399001'},
        {'name': '创业板指', 'secid': '0.399006'},
    ]
    
    results = []
    for idx in indices:
        url = f'https://push2.eastmoney.com/api/qt/stock/get?secid={idx["secid"]}&fields=f43,f169,f170'
        try:
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if data.get('rc') == 0 and data.get('data'):
                d = data['data']
                results.append({
                    'name': idx['name'],
                    'current': d.get('f43', 0) / 100,
                    'change_pct': d.get('f170', 0) / 100,
                })
        except:
            pass
    return results

def calculate_sentiment(indices):
    """计算市场情绪"""
    if not indices:
        return 50, '⚪ 中性 (数据获取中)'
    
    avg_change = sum(i['change_pct'] for i in indices) / len(indices)
    
    if avg_change > 1:
        return 80, '🟢 乐观'
    elif avg_change > 0.5:
        return 65, '🟡 偏乐观'
    elif avg_change > -0.5:
        return 50, '⚪ 中性'
    elif avg_change > -1:
        return 35, '🟡 偏悲观'
    else:
        return 20, '🔴 悲观'

def generate_report():
    """生成飞书消息内容"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 获取数据
    indices = get_market_indices()
    sentiment_score, sentiment_level = calculate_sentiment(indices)
    
    # 构建消息
    lines = []
    lines.append(f"📈 **A 股持仓日报** - {timestamp}")
    lines.append("")
    lines.append(f"**市场情绪**: {sentiment_score}/100 {sentiment_level}")
    lines.append("")
    lines.append("**大盘指数**:")
    for idx in indices:
        symbol = "🟢" if idx['change_pct'] >= 0 else "🔴"
        lines.append(f"  {symbol} {idx['name']}: {idx['current']:.2f} ({idx['change_pct']:+.2f}%)")
    lines.append("")
    lines.append("**持仓股票**:")
    
    for stock in STOCKS:
        data = get_stock_data(stock['code'], stock['market'])
        if data:
            # 处理负数成本（做 T 成功）
            if stock['cost'] < 0:
                profit_pct = abs(data['current'] - abs(stock['cost'])) / abs(stock['cost']) * 100
                profit_display = f"成本负数 (做 T 成功)"
            else:
                profit_pct = ((data['current'] - stock['cost']) / stock['cost']) * 100
                profit_display = f"{profit_pct:+.1f}%"
            
            profit_symbol = "🟢" if profit_pct >= 0 else "🔴"
            change_symbol = "🟢" if data['change_pct'] >= 0 else "🔴"
            
            lines.append(f"  {profit_symbol} **{stock['name']}**: ¥{data['current']:.2f} ({profit_display}) | 今日 {change_symbol}{data['change_pct']:+.2f}%")
    
    lines.append("")
    lines.append("**操作建议**:")
    lines.append("  🟢 中国卫通、恒逸石化：持有/加仓")
    lines.append("  🟡 汉缆股份、广电电气、中矿资源：持有")
    lines.append("")
    lines.append(f"**整体仓位**: 60% (防守为主)")
    lines.append("")
    lines.append("_详情查看：~/workspace/stock_dashboard.html_")
    
    return "\n".join(lines)

def send_feishu_message(content):
    """发送飞书消息"""
    payload = {
        "msg_type": "text",
        "content": {
            "text": content
        }
    }
    
    try:
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        return resp.status_code == 200
    except:
        return False

if __name__ == '__main__':
    print("📊 生成飞书日报...")
    content = generate_report()
    print(content)
    print("\n📱 发送飞书消息...")
    success = send_feishu_message(content)
    if success:
        print("✅ 飞书日报已发送")
    else:
        print("❌ 发送失败")

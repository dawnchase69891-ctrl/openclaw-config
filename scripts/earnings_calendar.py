# 持仓股票 - 从统一配置导入
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.expanduser('~/.openclaw/workspace/stock_database.db')

try:
    import sys
    sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/skills/a-stock-monitor/scripts'))
    from portfolio_config import PORTFOLIO as _PORTFOLIO
    STOCKS = [
        {'code': s['code'], 'name': s['name'], 'sector': s.get('industry', '')}
        for s in _PORTFOLIO if s.get('type', 'stock') == 'stock'
    ]
except Exception:
    # 降级配置
    STOCKS = [
        {'code': '000703', 'name': '恒逸石化', 'sector': '石化'},
        {'code': '002498', 'name': '汉缆股份', 'sector': '电力设备'},
        {'code': '002738', 'name': '中矿资源', 'sector': '有色金属'},
        {'code': '601616', 'name': '广电电气', 'sector': '电气设备'},
        {'code': '601698', 'name': '中国卫通', 'sector': '航天航空'},
    ]

def fetch_earnings_calendar():
    """获取财报日历"""
    earnings = []
    
    # 使用东方财富 API 获取财报日历
    # 注意：这是示例，实际需要更完整的 API 调用
    for stock in STOCKS:
        code = stock['code']
        
        # 示例：估算财报日期（实际需要 API）
        # A 股财报披露时间：
        # 年报：1 月 1 日 -4 月 30 日
        # 一季报：4 月 1 日 -4 月 30 日
        # 中报：7 月 1 日 -8 月 31 日
        # 三季报：10 月 1 日 -10 月 31 日
        
        current_month = datetime.now().month
        
        # 估算下一个财报季
        if current_month <= 3:
            # 年报 + 一季报季
            report_type = '年报/一季报'
            est_date = datetime.now().replace(month=3, day=31)
        elif current_month <= 6:
            # 中报季
            report_type = '中报'
            est_date = datetime.now().replace(month=7, day=31)
        elif current_month <= 9:
            # 三季报季
            report_type = '三季报'
            est_date = datetime.now().replace(month=10, day=31)
        else:
            # 年报季
            report_type = '年报'
            est_date = datetime.now().replace(year=datetime.now().year + 1, month=3, day=31)
        
        earnings.append({
            'code': code,
            'name': stock['name'],
            'type': report_type,
            'estimated_date': est_date.strftime('%Y-%m-%d'),
        })
    
    return earnings

def save_earnings_to_calendar(earnings):
    """保存财报到日历"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 确保 event_calendar 表存在
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            stock_name TEXT,
            scheduled_date TEXT NOT NULL,
            actual_date TEXT,
            status TEXT DEFAULT 'scheduled',
            summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    for earning in earnings:
        # 检查是否已存在
        cursor.execute('''
            SELECT id FROM event_calendar
            WHERE event_type = '财报' AND stock_code = ? AND scheduled_date = ?
        ''', (earning['code'], earning['estimated_date']))
        
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO event_calendar (
                    event_type, stock_code, stock_name, scheduled_date, summary
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                '财报',
                earning['code'],
                earning['name'],
                earning['estimated_date'],
                f"{earning['type']}预计披露"
            ))
            print(f"  ✅ 添加：{earning['code']} {earning['name']} {earning['type']} ({earning['estimated_date']})")
        else:
            print(f"  ⏭️  已存在：{earning['code']}")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("=" * 80)
    print("📅 财报日历获取器")
    print("=" * 80)
    
    print("\n📡 获取财报日历...")
    earnings = fetch_earnings_calendar()
    
    print(f"\n💾 保存到日历...")
    save_earnings_to_calendar(earnings)
    
    print(f"\n✅ 完成！共 {len(earnings)} 只股票")

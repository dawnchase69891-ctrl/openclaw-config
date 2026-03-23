# 持仓股票 - 从统一配置导入
try:
    import sys
    import os
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

# 警报规则
ALERT_RULES = {
    '股价异动': {
        'condition': lambda change_pct: abs(change_pct) > 5,
        'level': 'high',
        'message': '股价异动：涨跌幅超过 5%'
    },
    '主力大幅流入': {
        'condition': lambda inflow: inflow > 50000000,
        'level': 'medium',
        'message': '主力大幅流入：超过 5000 万'
    },
    '主力大幅流出': {
        'condition': lambda inflow: inflow < -50000000,
        'level': 'high',
        'message': '主力大幅流出：超过 5000 万'
    },
    '突破目标价': {
        'condition': lambda current, target: current >= target,
        'level': 'medium',
        'message': '突破目标价'
    },
    '跌破止损价': {
        'condition': lambda current, stop: current <= stop,
        'level': 'high',
        'message': '跌破止损价！'
    },
    '情绪极端乐观': {
        'condition': lambda score: score > 80,
        'level': 'medium',
        'message': '市场情绪极端乐观'
    },
    '情绪极端悲观': {
        'condition': lambda score: score < 20,
        'level': 'high',
        'message': '市场情绪极端悲观！'
    }
}


def init_events_table():
    """初始化事件表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 确保 events 表存在
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            stock_code TEXT,
            stock_name TEXT,
            event_date TEXT NOT NULL,
            impact TEXT,
            summary TEXT NOT NULL,
            source TEXT,
            url TEXT,
            is_alert INTEGER DEFAULT 0,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 警报历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alert_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type TEXT NOT NULL,
            stock_code TEXT,
            stock_name TEXT,
            alert_level TEXT NOT NULL,
            message TEXT NOT NULL,
            current_price REAL,
            trigger_value REAL,
            is_sent INTEGER DEFAULT 0,
            sent_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 事件日历表
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
    
    conn.commit()
    conn.close()
    print("✅ 事件追踪表已初始化")


def insert_event(event_data):
    """插入事件记录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO events (
            event_type, stock_code, stock_name, event_date,
            impact, summary, source, url, is_alert
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        event_data['event_type'],
        event_data['stock_code'],
        event_data['stock_name'],
        event_data['event_date'],
        event_data['impact'],
        event_data['summary'],
        event_data.get('source', '系统'),
        event_data.get('url', ''),
        event_data.get('is_alert', 0)
    ))
    
    conn.commit()
    conn.close()


def insert_alert(alert_data):
    """插入警报记录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO alert_history (
            alert_type, stock_code, stock_name, alert_level,
            message, current_price, trigger_value, is_sent, sent_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        alert_data['alert_type'],
        alert_data['stock_code'],
        alert_data['stock_name'],
        alert_data['alert_level'],
        alert_data['message'],
        alert_data.get('current_price'),
        alert_data.get('trigger_value'),
        alert_data.get('is_sent', 0),
        alert_data.get('sent_at')
    ))
    
    conn.commit()
    conn.close()


def check_price_alerts(stock_data, recommendations):
    """检查价格相关警报"""
    alerts = []
    
    for stock in stock_data:
        code = stock['code']
        name = stock['name']
        current = stock['current']
        change_pct = stock['change_pct']
        inflow = stock.get('main_net_inflow', 0)
        
        # 获取建议中的目标价和止损价
        rec = next((r for r in recommendations if r['stock_code'] == code), None)
        if not rec:
            continue
        
        target = rec.get('target_price', 0)
        stop_loss = rec.get('stop_loss', 0)
        
        # 检查各警报规则
        for rule_name, rule in ALERT_RULES.items():
            triggered = False
            trigger_value = None
            
            if rule_name == '股价异动':
                triggered = rule['condition'](change_pct)
                trigger_value = change_pct
            elif rule_name == '主力大幅流入':
                triggered = rule['condition'](inflow)
                trigger_value = inflow
            elif rule_name == '主力大幅流出':
                triggered = rule['condition'](inflow)
                trigger_value = inflow
            elif rule_name == '突破目标价':
                triggered = rule['condition'](current, target)
                trigger_value = target
            elif rule_name == '跌破止损价':
                triggered = rule['condition'](current, stop_loss)
                trigger_value = stop_loss
            
            if triggered:
                alert = {
                    'alert_type': rule_name,
                    'stock_code': code,
                    'stock_name': name,
                    'alert_level': rule['level'],
                    'message': f"{name} ({code}): {rule['message']}",
                    'current_price': current,
                    'trigger_value': trigger_value,
                }
                alerts.append(alert)
                
                # 记录到数据库
                insert_alert(alert)
    
    return alerts


def check_sentiment_alert(sentiment_score):
    """检查市场情绪警报"""
    alerts = []
    
    if sentiment_score > 80:
        alert = {
            'alert_type': '情绪极端乐观',
            'stock_code': 'MARKET',
            'stock_name': '全市场',
            'alert_level': 'medium',
            'message': f'市场情绪极端乐观：{sentiment_score}/100',
            'current_price': sentiment_score,
            'trigger_value': 80,
        }
        alerts.append(alert)
        insert_alert(alert)
    elif sentiment_score < 20:
        alert = {
            'alert_type': '情绪极端悲观',
            'stock_code': 'MARKET',
            'stock_name': '全市场',
            'alert_level': 'high',
            'message': f'市场情绪极端悲观：{sentiment_score}/100',
            'current_price': sentiment_score,
            'trigger_value': 20,
        }
        alerts.append(alert)
        insert_alert(alert)
    
    return alerts


def fetch_earnings_calendar():
    """获取财报日历"""
    events = []
    
    # 这里可以接入财报日历 API
    # 示例：手动添加已知财报日期
    earnings = [
        # 示例数据，实际需要 API 获取
        # {'code': '000703', 'date': '2026-03-15', 'type': '年报'},
    ]
    
    for earning in earnings:
        event = {
            'event_type': '财报',
            'stock_code': earning['code'],
            'stock_name': next((s['name'] for s in STOCKS if s['code'] == earning['code']), ''),
            'event_date': earning['date'],
            'impact': '未知',
            'summary': f"{earning['type']}公布",
            'source': '财报日历',
            'is_alert': 0
        }
        events.append(event)
        insert_event(event)
    
    return events


def fetch_policy_news():
    """获取政策新闻"""
    events = []
    
    # 关键词
    keywords = ['两会', '新能源', '商业航天', '电力设备', '石化']
    
    # 这里可以接入新闻 API
    # 示例：手动添加
    
    return events


def send_alert_message(alerts):
    """发送警报消息"""
    if not alerts:
        return
    
    message = "🚨 **警报通知**\n\n"
    
    for alert in alerts:
        level_emoji = '🔴' if alert['alert_level'] == 'high' else '🟡'
        message += f"{level_emoji} {alert['message']}\n"
    
    message += f"\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # 这里可以集成飞书消息推送
    print("\n📱 警报消息:")
    print(message)
    
    # 更新已发送状态
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for alert in alerts:
        cursor.execute('''
            UPDATE alert_history
            SET is_sent = 1, sent_at = ?
            WHERE alert_type = ? AND stock_code = ? AND created_at = (
                SELECT MAX(created_at) FROM alert_history
                WHERE alert_type = ? AND stock_code = ?
            )
        ''', (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            alert['alert_type'],
            alert['stock_code'],
            alert['alert_type'],
            alert['stock_code']
        ))
    
    conn.commit()
    conn.close()


def get_upcoming_events(days=7):
    """获取未来 N 天的事件"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    future_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        cursor.execute('''
            SELECT event_type, stock_code, stock_name, event_date, summary
            FROM events
            WHERE event_date >= ? AND event_date <= ?
            ORDER BY event_date
        ''', (today, future_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        return rows
    except sqlite3.OperationalError:
        # 表可能不存在或字段不匹配
        conn.close()
        return []


if __name__ == '__main__':
    print("=" * 80)
    print("🚨 事件追踪与智能警报系统 - 阶段 3")
    print("=" * 80)
    
    # 初始化表
    init_events_table()
    
    # 测试数据
    test_stock_data = [
        {
            'code': '000703',
            'name': '恒逸石化',
            'current': 13.09,
            'change_pct': 13.09,
            'main_net_inflow': 50000000,
        },
        {
            'code': '002498',
            'name': '汉缆股份',
            'current': 8.94,
            'change_pct': 0.00,
            'main_net_inflow': 0,
        },
        {
            'code': '002738',
            'name': '中矿资源',
            'current': 79.71,
            'change_pct': 13.87,
            'main_net_inflow': 30000000,
        },
        {
            'code': '601616',
            'name': '广电电气',
            'current': 5.56,
            'change_pct': 0.72,
            'main_net_inflow': 10000000,
        },
        {
            'code': '601698',
            'name': '中国卫通',
            'current': 37.05,
            'change_pct': 37.05,
            'main_net_inflow': 120000000,
        }
    ]
    
    test_recommendations = [
        {
            'stock_code': '000703',
            'target_price': 13.50,
            'stop_loss': 11.00,
        },
        {
            'stock_code': '002498',
            'target_price': 9.50,
            'stop_loss': 8.00,
        },
        {
            'stock_code': '002738',
            'target_price': 88.00,
            'stop_loss': 72.00,
        },
        {
            'stock_code': '601616',
            'target_price': 6.00,
            'stop_loss': 5.00,
        },
        {
            'stock_code': '601698',
            'target_price': 40.50,
            'stop_loss': 35.80,
        }
    ]
    
    print("\n🔍 检查价格警报...")
    alerts = check_price_alerts(test_stock_data, test_recommendations)
    
    if alerts:
        print(f"✅ 触发 {len(alerts)} 条警报:")
        for alert in alerts:
            level = '🔴' if alert['alert_level'] == 'high' else '🟡'
            print(f"  {level} {alert['message']}")
    else:
        print("✅ 无触发警报")
    
    print("\n🌡️ 检查市场情绪警报...")
    sentiment_alerts = check_sentiment_alert(50)
    
    if sentiment_alerts:
        for alert in sentiment_alerts:
            print(f"  {alert['message']}")
    else:
        print("  情绪正常")
    
    print("\n📅 获取未来事件...")
    upcoming = get_upcoming_events(days=7)
    
    if upcoming:
        for event in upcoming:
            print(f"  {event[3]} {event[0]} {event[1]} {event[2]}: {event[4]}")
    else:
        print("  无即将发生的事件")
    
    print("\n✅ 阶段 3 系统就绪！")

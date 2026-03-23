#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融 Agent 数据库 - 阶段 1
创建 SQLite 数据库，记录交易建议和历史表现
"""

import sqlite3
import json
from datetime import datetime
import os

DB_PATH = os.path.expanduser('~/.openclaw/workspace/stock_database.db')

def create_database():
    """创建数据库和表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 交易建议历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL,
            action TEXT NOT NULL,
            target_price REAL,
            stop_loss REAL,
            position_pct REAL,
            confidence TEXT,
            current_price REAL NOT NULL,
            cost_basis REAL NOT NULL,
            profit_pct REAL NOT NULL,
            change_pct REAL NOT NULL,
            main_net_inflow REAL,
            sector TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 策略绩效表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strategy_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_name TEXT NOT NULL,
            total_trades INTEGER DEFAULT 0,
            win_trades INTEGER DEFAULT 0,
            win_rate REAL DEFAULT 0,
            avg_return_1d REAL DEFAULT 0,
            avg_return_3d REAL DEFAULT 0,
            avg_return_5d REAL DEFAULT 0,
            max_drawdown REAL DEFAULT 0,
            sharpe_ratio REAL DEFAULT 0,
            last_updated TEXT
        )
    ''')
    
    # 市场情绪历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            score INTEGER NOT NULL,
            level TEXT NOT NULL,
            sh_index REAL,
            sz_index REAL,
            cyb_index REAL,
            hs300_index REAL,
            gainers INTEGER,
            losers INTEGER,
            limit_up INTEGER,
            limit_down INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 持仓快照表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio_snapshot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL,
            current_price REAL NOT NULL,
            cost_basis REAL NOT NULL,
            profit_pct REAL NOT NULL,
            change_pct REAL NOT NULL,
            position_pct REAL,
            main_net_inflow REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 事件追踪表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            stock_code TEXT,
            event_date TEXT NOT NULL,
            impact TEXT,
            summary TEXT NOT NULL,
            source TEXT,
            url TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rec_date ON recommendations(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rec_stock ON recommendations(stock_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sentiment_date ON sentiment_history(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_portfolio_date ON portfolio_snapshot(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ 数据库已创建：{DB_PATH}")

def insert_recommendation(data):
    """插入交易建议记录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO recommendations (
            date, timestamp, stock_code, stock_name, action,
            target_price, stop_loss, position_pct, confidence,
            current_price, cost_basis, profit_pct, change_pct,
            main_net_inflow, sector, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('date'),
        data.get('timestamp'),
        data.get('stock_code'),
        data.get('stock_name'),
        data.get('action'),
        data.get('target_price'),
        data.get('stop_loss'),
        data.get('position_pct'),
        data.get('confidence'),
        data.get('current_price'),
        data.get('cost_basis'),
        data.get('profit_pct'),
        data.get('change_pct'),
        data.get('main_net_inflow'),
        data.get('sector'),
        data.get('notes')
    ))
    
    conn.commit()
    conn.close()
    print(f"✅ 已记录建议：{data['stock_code']} {data['action']}")

def insert_sentiment(data):
    """插入市场情绪记录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sentiment_history (
            date, timestamp, score, level,
            sh_index, sz_index, cyb_index, hs300_index,
            gainers, losers, limit_up, limit_down, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('date'),
        data.get('timestamp'),
        data.get('score'),
        data.get('level'),
        data.get('sh_index'),
        data.get('sz_index'),
        data.get('cyb_index'),
        data.get('hs300_index'),
        data.get('gainers'),
        data.get('losers'),
        data.get('limit_up'),
        data.get('limit_down'),
        data.get('notes')
    ))
    
    conn.commit()
    conn.close()
    print(f"✅ 已记录情绪：{data['score']}/100 {data['level']}")

def insert_portfolio_snapshot(data):
    """插入持仓快照"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO portfolio_snapshot (
            date, timestamp, stock_code, stock_name,
            current_price, cost_basis, profit_pct, change_pct,
            position_pct, main_net_inflow
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('date'),
        data.get('timestamp'),
        data.get('stock_code'),
        data.get('stock_name'),
        data.get('current_price'),
        data.get('cost_basis'),
        data.get('profit_pct'),
        data.get('change_pct'),
        data.get('position_pct'),
        data.get('main_net_inflow')
    ))
    
    conn.commit()
    conn.close()

def get_recommendations_history(stock_code=None, limit=30):
    """获取历史建议"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if stock_code:
        cursor.execute('''
            SELECT * FROM recommendations
            WHERE stock_code = ?
            ORDER BY date DESC, timestamp DESC
            LIMIT ?
        ''', (stock_code, limit))
    else:
        cursor.execute('''
            SELECT * FROM recommendations
            ORDER BY date DESC, timestamp DESC
            LIMIT ?
        ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def get_performance_summary():
    """获取绩效统计"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN profit_pct > 0 THEN 1 ELSE 0 END) as wins,
            AVG(profit_pct) as avg_profit,
            MAX(profit_pct) as max_profit,
            MIN(profit_pct) as min_profit
        FROM recommendations
    ''')
    
    row = cursor.fetchone()
    conn.close()
    
    return {
        'total': row[0],
        'wins': row[1],
        'win_rate': row[1]/row[0]*100 if row[0] > 0 else 0,
        'avg_profit': row[2],
        'max_profit': row[3],
        'min_profit': row[4]
    }

if __name__ == '__main__':
    print("📊 金融 Agent 数据库初始化")
    print("=" * 50)
    
    # 创建数据库
    create_database()
    
    # 测试插入
    print("\n📝 测试数据插入...")
    
    test_rec = {
        'date': '2026-03-02',
        'timestamp': '2026-03-02 10:17',
        'stock_code': '601698',
        'stock_name': '中国卫通',
        'action': '🟢 持有/加仓',
        'target_price': 42.00,
        'stop_loss': 36.00,
        'position_pct': 80,
        'confidence': '高',
        'current_price': 39.52,
        'cost_basis': 37.16,
        'profit_pct': 6.35,
        'change_pct': 5.89,
        'main_net_inflow': 121914208,
        'sector': '卫星互联网',
        'notes': '唯一逆势上涨，主力大幅流入'
    }
    
    insert_recommendation(test_rec)
    
    test_sentiment = {
        'date': '2026-03-02',
        'timestamp': '2026-03-02 10:17',
        'score': 50,
        'level': '中性偏空',
        'sh_index': 4134.70,
        'sz_index': 14302.22,
        'cyb_index': 3264.43,
        'hs300_index': 4670.99,
        'gainers': 0,
        'losers': 0,
        'limit_up': 0,
        'limit_down': 0,
        'notes': '市场普跌'
    }
    
    insert_sentiment(test_sentiment)
    
    print("\n✅ 数据库初始化完成！")
    print(f"📂 数据库位置：{DB_PATH}")

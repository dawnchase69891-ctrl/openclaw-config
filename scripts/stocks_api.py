#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票管理 API
提供添加/删除股票的 HTTP API 接口
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

CONFIG_PATH = os.path.expanduser('~/.openclaw/workspace/config.json')

def load_config():
    """加载配置文件"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """保存配置文件"""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def add_stock(stock_type: str, stock_data: dict) -> dict:
    """添加股票"""
    # 参数验证
    if stock_type not in ['portfolio', 'watchlist']:
        return {'success': False, 'message': '无效的股票类型，必须是 portfolio 或 watchlist'}
    
    if not stock_data.get('code') or len(stock_data['code']) != 6:
        return {'success': False, 'message': '股票代码必须是 6 位数字'}
    
    if not stock_data.get('name'):
        return {'success': False, 'message': '股票名称不能为空'}
    
    config = load_config()
    
    if stock_type == 'portfolio':
        # 检查是否已存在
        for stock in config.get('portfolio', {}).get('stocks', []):
            if stock['code'] == stock_data['code']:
                return {'success': False, 'message': '该股票已在持仓列表中'}
        
        # 添加持仓股
        if 'stocks' not in config.get('portfolio', {}):
            config['portfolio']['stocks'] = []
        
        config['portfolio']['stocks'].append({
            'code': stock_data['code'],
            'name': stock_data['name'],
            'cost': stock_data.get('cost', 0),
            'market': stock_data.get('market', 'sz')
        })
        
    elif stock_type == 'watchlist':
        # 检查是否已存在
        for stock in config.get('portfolio', {}).get('watchlist', []):
            if stock['code'] == stock_data['code']:
                return {'success': False, 'message': '该股票已在自选列表中'}
        
        # 添加自选股
        if 'watchlist' not in config.get('portfolio', {}):
            config['portfolio']['watchlist'] = []
        
        config['portfolio']['watchlist'].append({
            'code': stock_data['code'],
            'name': stock_data['name'],
            'reason': stock_data.get('reason', ''),
            'market': stock_data.get('market', 'sz')
        })
    
    save_config(config)
    
    # 记录到 learnings
    log_action('add', stock_type, stock_data['code'], stock_data['name'])
    
    return {'success': True, 'message': '添加成功'}

def delete_stock(stock_type: str, code: str) -> dict:
    """删除股票"""
    config = load_config()
    deleted_name = ''
    
    if stock_type == 'portfolio':
        stocks = config.get('portfolio', {}).get('stocks', [])
        for i, stock in enumerate(stocks):
            if stock['code'] == code:
                deleted_name = stock['name']
                stocks.pop(i)
                break
        else:
            return {'success': False, 'message': '未找到该股票'}
        
    elif stock_type == 'watchlist':
        stocks = config.get('portfolio', {}).get('watchlist', [])
        for i, stock in enumerate(stocks):
            if stock['code'] == code:
                deleted_name = stock['name']
                stocks.pop(i)
                break
        else:
            return {'success': False, 'message': '未找到该股票'}
    
    save_config(config)
    
    # 记录到 learnings
    log_action('delete', stock_type, code, deleted_name)
    
    return {'success': True, 'message': '删除成功'}

def log_action(action: str, stock_type: str, code: str, name: str):
    """记录操作到 learnings 文件"""
    learnings_path = os.path.expanduser('~/.openclaw/workspace/.learnings/LEARNINGS.md')
    
    timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
    entry_type = "portfolio_stock_added" if action == 'add' else "portfolio_stock_removed"
    stock_list_type = "持仓股" if stock_type == 'portfolio' else "自选股"
    action_text = "添加" if action == 'add' else "删除"
    
    entry = f"""
## [LRN-{datetime.now().strftime('%Y%m%d')}-{action.upper()[:3]}{code}] {entry_type}

**Logged**: {timestamp}
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
{action_text}{stock_list_type}: {code} {name}

### Details
- 操作类型：{action_text}
- 股票列表：{stock_list_type}
- 股票代码：{code}
- 股票名称：{name}

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, {action}
- Pattern-Key: portfolio.stock_{action}

---
"""
    
    try:
        with open(learnings_path, 'a', encoding='utf-8') as f:
            f.write(entry)
    except Exception as e:
        print(f"记录 learnings 失败：{e}")

class StocksAPIHandler(BaseHTTPRequestHandler):
    """HTTP API 处理器"""
    
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(200)
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/stocks/list':
            config = load_config()
            self._set_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'portfolio': config.get('portfolio', {}).get('stocks', []),
                'watchlist': config.get('portfolio', {}).get('watchlist', [])
            }, ensure_ascii=False).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())
    
    def do_POST(self):
        """处理 POST 请求"""
        parsed = urlparse(self.path)
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({'success': False, 'message': 'Invalid JSON'}).encode())
            return
        
        if parsed.path == '/api/stocks/add':
            stock_type = data.get('type')
            if stock_type not in ['portfolio', 'watchlist']:
                self._set_headers(400)
                self.wfile.write(json.dumps({'success': False, 'message': 'Invalid type'}).encode())
                return
            
            result = add_stock(stock_type, data)
            self._set_headers(200 if result['success'] else 400)
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode())
            
        elif parsed.path == '/api/stocks/delete':
            stock_type = data.get('type')
            code = data.get('code')
            
            if stock_type not in ['portfolio', 'watchlist'] or not code:
                self._set_headers(400)
                self.wfile.write(json.dumps({'success': False, 'message': 'Invalid parameters'}).encode())
                return
            
            result = delete_stock(stock_type, code)
            self._set_headers(200 if result['success'] else 400)
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[API] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {args[0]}")

def run_server(port=8080):
    """运行 API 服务器"""
    server = HTTPServer(('localhost', port), StocksAPIHandler)
    print(f"🚀 股票管理 API 已启动")
    print(f"📍 监听地址：http://localhost:{port}")
    print(f"📡 可用接口:")
    print(f"   GET  /api/stocks/list - 获取股票列表")
    print(f"   POST /api/stocks/add - 添加股票")
    print(f"   POST /api/stocks/delete - 删除股票")
    print(f"\n按 Ctrl+C 停止服务")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ 服务已停止")
        server.shutdown()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)

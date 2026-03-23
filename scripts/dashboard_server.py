#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驾驶舱数据 API 服务器
提供实时数据接口供 Web 看板调用
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from datetime import datetime
from pathlib import Path
import subprocess

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
DATA_FILE = WORKSPACE / 'dashboard_data.json'

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/data':
            self.send_json_response()
        elif self.path == '/api/refresh':
            self.refresh_data()
            self.send_json_response()
        else:
            super().do_GET()
    
    def send_json_response(self):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def refresh_data(self):
        try:
            subprocess.run(
                ['python3', str(WORKSPACE / 'scripts' / 'update_dashboard_data.py')],
                capture_output=True,
                timeout=30
            )
        except Exception as e:
            print(f"刷新失败：{e}")

def run_server(port=8888):
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"🚀 驾驶舱服务器启动")
    print(f"📊 看板地址：http://localhost:{port}/org_dashboard.html")
    print(f"📡 API 地址：http://localhost:{port}/api/data")
    print(f"🔄 刷新 API: http://localhost:{port}/api/refresh")
    print(f"按 Ctrl+C 停止服务")
    server.serve_forever()

if __name__ == '__main__':
    run_server()

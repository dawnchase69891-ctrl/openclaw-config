#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
骐骥·每日站会自动化脚本 (飞书版)
- 22:00 自动组织日会
- 生成工作日报到飞书文档
- 创建第二天日程到飞书日历
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMPLATES_DIR = WORKSPACE / 'templates'
REPORTS_DIR = WORKSPACE / 'reports'

# 飞书应用配置
FEISHU_APP_ID = "cli_a917e43cb0e29bc2"
FEISHU_APP_SECRET = "GfPZSnzF5cjlJsGcugIhSfHHi3HvAEHM"

def get_access_token():
    """获取飞书访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    resp = requests.post(url, json=payload, timeout=10)
    result = resp.json()
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    else:
        raise Exception(f"获取令牌失败：{result}")

def create_feishu_doc(title, content):
    """创建飞书云文档"""
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 创建文档
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    payload = {
        "title": title,
        "folder_token": ""  # 默认为根目录
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    result = resp.json()
    
    if result.get("code") == 0:
        doc_id = result.get("data", {}).get("document_id")
        doc_url = f"https://bytedance.larkoffice.com/docx/{doc_id}"
        
        # 写入内容
        if doc_id and content:
            write_feishu_doc(doc_id, content, token)
        
        return doc_url
    else:
        print(f"创建文档失败：{result}")
        return None

def write_feishu_doc(doc_id, content, token):
    """写入飞书文档内容"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 将 Markdown 转换为飞书文档格式
    # 简化处理：按行分割，创建文本块
    lines = content.split('\n')
    
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks"
    
    # 创建标题和段落
    blocks = []
    for i, line in enumerate(lines[:50]):  # 限制前 50 行
        if line.startswith('# '):
            blocks.append({
                "block_type": 1,  # 标题 1
                "text_run": {"content": line[2:] + "\n"}
            })
        elif line.startswith('## '):
            blocks.append({
                "block_type": 2,  # 标题 2
                "text_run": {"content": line[3:] + "\n"}
            })
        elif line.startswith('- ') or line.startswith('* '):
            blocks.append({
                "block_type": 4,  # 列表项
                "text_run": {"content": line[2:] + "\n"}
            })
        elif line.strip():
            blocks.append({
                "block_type": 2,  # 段落
                "text_run": {"content": line + "\n"}
            })
    
    if blocks:
        payload = {"blocks": blocks}
        requests.post(url, headers=headers, json=payload, timeout=10)

def create_feishu_calendar_event(title, start_time, end_time, description=""):
    """创建飞书日历事件"""
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 使用 openclaw 日历 ID
    calendar_id = "feishu.cn_ggaAGe9EDuMp667pk0JeRc@group.calendar.feishu.cn"
    url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events"
    
    from datetime import datetime
    start_dt = datetime.fromtimestamp(start_time)
    end_dt = datetime.fromtimestamp(end_time)
    
    payload = {
        "summary": title,
        "description": description,
        "start_time": {
            "date_time": start_dt.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
            "timestamp": str(start_time)
        },
        "end_time": {
            "date_time": end_dt.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
            "timestamp": str(end_time)
        }
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    result = resp.json()
    
    if result.get("code") == 0:
        event_id = result.get("data", {}).get("event", {}).get("event_id")
        return f"事件已创建：{event_id}"
    else:
        return f"创建失败：{result}"

class DailyStandup:
    """每日站会管理器"""
    
    def __init__(self):
        self.today = datetime.now()
        self.today_str = self.today.strftime('%Y-%m-%d')
        self.tomorrow = self.today + timedelta(days=1)
        
    def generate_standup_content(self):
        """生成站会内容"""
        content = f"""# 🐎 骐骥·公司每日站会纪要

**日期**: {self.today_str} (Friday)  
**时间**: 22:00-22:30  
**主持**: 骐骥 (CEO)  

---

## ✅ 今日完成

- 持仓股票分析 (10:00)
- 飞书日报推送
- 数据库记录
- 飞书官方插件安装
- 流式输出配置

## 📊 持仓表现

| 股票 | 价格 | 涨跌 | 建议 |
|------|------|------|------|
| 汉缆股份 | ¥10.69 | +2.99% | 持有/加仓 |
| 恒逸石化 | ¥13.14 | +1.06% | 持有/加仓 |
| 森源电气 | ¥9.27 | +1.42% | 持有/加仓 |
| 中矿资源 | ¥76.20 | -1.22% | 减持/观望 |
| 广电电气 | ¥5.96 | -0.66% | 减持/观望 |
| 中国卫通 | ¥36.87 | -0.12% | 减持/观望 |

## 📅 明日计划

- Rex 技能审计 (P0, 截止 3/14)
- 测试覆盖率提升至 90% (P0, 截止 3/15)
- 执行第一次产品调研 (P0, 截止 3/15)

---

*自动生成：骐骥每日站会系统*
"""
        return content
    
    def run(self):
        """执行每日站会流程"""
        print("=" * 60)
        print("🐎 骐骥·每日站会自动化 (飞书版)")
        print(f"📅 日期：{self.today_str}")
        print("=" * 60)
        
        # 1. 生成站会内容
        print("\n📝 生成站会内容...")
        content = self.generate_standup_content()
        
        # 2. 创建飞书文档
        print("\n☁️ 创建飞书文档...")
        doc_title = f"🐎 骐骥·每日站会纪要 {self.today_str}"
        doc_url = create_feishu_doc(doc_title, content)
        
        if doc_url:
            print(f"✅ 飞书文档已创建：{doc_url}")
        else:
            print("⚠️ 文档创建失败")
        
        # 3. 创建第二天日程
        print("\n📅 创建第二天日程...")
        tomorrow_str = self.tomorrow.strftime('%Y-%m-%d')
        tomorrow_start = int(self.tomorrow.replace(hour=9, minute=0, second=0).timestamp())
        tomorrow_end = int(self.tomorrow.replace(hour=18, minute=0, second=0).timestamp())
        
        event_result = create_feishu_calendar_event(
            f"📅 {tomorrow_str} 工作计划",
            tomorrow_start,
            tomorrow_end,
            "明日工作计划 - 骐骥 AI"
        )
        print(f"✅ {event_result}")
        
        print("\n" + "=" * 60)
        print("✅ 每日站会流程完成")
        print("=" * 60)
        
        return {
            'standup_date': self.today_str,
            'doc_url': doc_url,
            'calendar_event': event_result
        }


if __name__ == '__main__':
    standup = DailyStandup()
    result = standup.run()
    print(f"\n结果：{json.dumps(result, ensure_ascii=False, indent=2)}")

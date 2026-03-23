#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书爬虫 - OpenClaw Browser 工具集成版
赤兔计划 (RED-RABBIT) - 任务 ID: recvetJHM0itG2

此脚本通过 OpenClaw 的 browser 工具进行抓取
使用方式：通过 OpenClaw 的 sessions_spawn 或直接调用

功能：
1. 使用 OpenClaw browser 工具打开小红书
2. 搜索养生关键词
3. 抓取笔记数据
4. 存储到飞书多维表格
"""

import asyncio
import json
import time
import random
from datetime import datetime
from typing import List, Dict, Any, Optional


# ============================================================================
# 配置
# ============================================================================

class XHSConfig:
    """爬虫配置"""
    
    # 飞书多维表格
    BITABLE_APP_TOKEN = "MxDxb1YyDair5XsO28Yc2WcknTe"
    BITABLE_TABLE_ID = "tblDKbuvCtBn3eew"
    
    # 搜索关键词
    KEYWORDS = ["养生茶", "药食同源", "食疗"]
    
    # 抓取限制
    MAX_NOTES_PER_KEYWORD = 20
    
    # 延迟设置（秒）
    MIN_DELAY = 2
    MAX_DELAY = 5


# ============================================================================
# 数据模型
# ============================================================================

class NoteRecord:
    """笔记记录"""
    
    def __init__(self):
        self.note_id = ""
        self.title = ""
        self.cover_image = ""
        self.author = ""
        self.author_id = ""
        self.likes = 0
        self.collects = 0
        self.comments = 0
        self.content = ""
        self.tags = []
        self.publish_time = None
        self.url = ""
        self.keyword = ""
        self.crawl_time = datetime.now().isoformat()
    
    def to_feishu_fields(self) -> Dict[str, Any]:
        """转换为飞书字段"""
        return {
            "笔记 ID": self.note_id,
            "标题": self.title,
            "封面图": self.cover_image,
            "作者": self.author,
            "作者 ID": self.author_id,
            "点赞数": self.likes,
            "收藏数": self.collects,
            "评论数": self.comments,
            "完整文案": self.content,
            "标签": ", ".join(self.tags),
            "发布时间": int(datetime.now().timestamp() * 1000),
            "笔记链接": self.url,
            "搜索关键词": self.keyword,
            "采集时间": self.crawl_time,
        }


# ============================================================================
# 爬虫类
# ============================================================================

class XiaohongshuCrawler:
    """小红书爬虫（OpenClaw Browser 工具版）"""
    
    def __init__(self):
        self.notes: List[NoteRecord] = []
        self.logs: List[str] = []
    
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        self.logs.append(log_line)
        print(log_line)
    
    def random_delay(self, min_sec: float = None, max_sec: float = None):
        """随机延迟"""
        min_sec = min_sec or XHSConfig.MIN_DELAY
        max_sec = max_sec or XHSConfig.MAX_DELAY
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def crawl_with_openclaw(self):
        """
        使用 OpenClaw browser 工具进行抓取
        
        这是一个示例实现，实际使用时需要通过 OpenClaw 的 sessions_spawn
        调用 browser 工具
        """
        self.log("=" * 60)
        self.log("🚀 小红书爆款内容采集 - OpenClaw Browser 工具版")
        self.log("=" * 60)
        
        # 注意：实际 browser 工具调用需要通过 OpenClaw 的 message 系统
        # 这里提供调用逻辑示例
        
        crawl_steps = [
            {
                "step": 1,
                "action": "browser",
                "params": {
                    "action": "open",
                    "url": "https://www.xiaohongshu.com",
                    "profile": "user"
                }
            },
            {
                "step": 2,
                "action": "browser",
                "params": {
                    "action": "snapshot",
                    "refs": "aria"
                }
            },
            # ... 更多步骤
        ]
        
        self.log("ℹ️  提示：此脚本需要通过 OpenClaw 的 browser 工具执行")
        self.log("ℹ️  请使用以下 OpenClaw 命令启动爬虫:")
        self.log("")
        self.log("openclaw exec --python scripts/xiaohongshu_crawler_openclaw.py")
        self.log("")
        self.log("或通过 OpenClaw 的 sessions_spawn 调用 browser 工具")
        
        return self.notes
    
    def save_to_feishu(self, notes: List[NoteRecord]) -> bool:
        """保存数据到飞书多维表格"""
        if not notes:
            self.log("⚠️  没有数据需要保存")
            return True
        
        self.log(f"💾 准备保存 {len(notes)} 条数据到飞书多维表格")
        
        # 准备批量创建的数据
        records = []
        for note in notes:
            records.append({
                "fields": note.to_feishu_fields()
            })
        
        # 输出导入指令
        self.log("")
        self.log("=" * 60)
        self.log("📋 飞书多维表格导入指令")
        self.log("=" * 60)
        self.log(f"App Token: {XHSConfig.BITABLE_APP_TOKEN}")
        self.log(f"Table ID: {XHSConfig.BITABLE_TABLE_ID}")
        self.log(f"记录数：{len(records)}")
        self.log("")
        self.log("请使用 feishu_bitable_app_table_record 工具:")
        self.log("  action: batch_create")
        self.log(f"  app_token: {XHSConfig.BITABLE_APP_TOKEN}")
        self.log(f"  table_id: {XHSConfig.BITABLE_TABLE_ID}")
        self.log("  records: [上述 records 数组]")
        
        return True
    
    def export_logs(self) -> str:
        """导出日志"""
        return "\n".join(self.logs)


# ============================================================================
# OpenClaw Browser 工具调用示例
# ============================================================================

def get_browser_commands() -> List[Dict[str, Any]]:
    """
    获取 OpenClaw browser 工具调用命令序列
    
    Returns:
        命令列表
    """
    commands = []
    
    # 1. 打开小红书
    commands.append({
        "tool": "browser",
        "action": "open",
        "params": {
            "action": "open",
            "url": "https://www.xiaohongshu.com",
            "profile": "user",
            "target": "host"
        }
    })
    
    # 2. 等待页面加载
    commands.append({
        "tool": "browser",
        "action": "snapshot",
        "params": {
            "action": "snapshot",
            "refs": "aria",
            "timeoutMs": 10000
        }
    })
    
    # 3. 搜索关键词
    for keyword in XHSConfig.KEYWORDS[:1]:  # 测试用第一个关键词
        commands.append({
            "tool": "browser",
            "action": "navigate",
            "params": {
                "action": "navigate",
                "url": f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes"
            }
        })
        
        # 4. 获取页面快照
        commands.append({
            "tool": "browser",
            "action": "snapshot",
            "params": {
                "action": "snapshot",
                "refs": "aria",
                "timeoutMs": 5000
            }
        })
        
        # 5. 提取笔记链接（需要通过 evaluate 执行 JS）
        commands.append({
            "tool": "browser",
            "action": "act",
            "params": {
                "action": "act",
                "kind": "evaluate",
                "fn": """() => {
                    const links = document.querySelectorAll('a[href*="/explore/"]');
                    const urls = [];
                    links.forEach(link => {
                        const href = link.getAttribute('href');
                        if (href && !urls.includes(href)) {
                            urls.push(href);
                        }
                    });
                    return urls.slice(0, 20);
                }"""
            }
        })
    
    return commands


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    crawler = XiaohongshuCrawler()
    
    # 执行抓取
    crawler.crawl_with_openclaw()
    
    # 保存数据
    crawler.save_to_feishu(crawler.notes)
    
    # 输出日志
    print("\n" + "=" * 60)
    print("📄 抓取日志")
    print("=" * 60)
    print(crawler.export_logs())
    
    return crawler


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()

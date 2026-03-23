#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书爆款内容采集脚本 - 赤兔计划 (RED-RABBIT)
任务 ID: recvetJHM0itG2

功能：
1. 使用浏览器自动化抓取小红书养生领域爆款内容
2. 搜索关键词："养生茶"、"药食同源"、"食疗"等
3. 采集笔记信息：标题、封面图、作者、点赞数、收藏数、完整文案、标签、发布时间
4. 存储到飞书多维表格

技术栈：
- Playwright: 浏览器自动化（模拟 OpenClaw browser 工具行为）
- Feishu Bitable API: 数据存储
- asyncio: 异步并发控制

作者：ClawBuilder
创建日期：2026-03-21
"""

import asyncio
import random
import time
import json
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

try:
    from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ 请安装 Playwright: pip install playwright")
    print("然后运行：playwright install")
    exit(1)

# ============================================================================
# 配置常量
# ============================================================================

class Config:
    """爬虫配置"""
    
    # 小红书相关
    XIAOHONGSHU_URL = "https://www.xiaohongshu.com"
    XIAOHONGSHU_SEARCH_URL = "https://www.xiaohongshu.com/search_result"
    
    # 搜索关键词列表
    KEYWORDS = ["养生茶", "药食同源", "食疗", "养生食谱", "健康饮食"]
    
    # 抓取控制
    MAX_NOTES_PER_KEYWORD = 20  # 每个关键词最多抓取笔记数
    SCROLL_PAUSE_MIN = 2  # 滚动页面最小延迟（秒）
    SCROLL_PAUSE_MAX = 5  # 滚动页面最大延迟（秒）
    REQUEST_DELAY_MIN = 3  # 请求间最小延迟（秒）
    REQUEST_DELAY_MAX = 6  # 请求间最大延迟（秒）
    
    # 浏览器配置
    HEADLESS = False  # 是否无头模式（建议 False，便于观察和手动登录）
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # 飞书多维表格配置
    FEISHU_BITABLE_APP_TOKEN = "MxDxb1YyDair5XsO28Yc2WcknTe"
    FEISHU_BITABLE_TABLE_ID = "tblDKbuvCtBn3eew"
    
    # 日志配置
    LOG_FILE = Path(__file__).parent / "xiaohongshu_crawler.log"
    DATA_EXPORT_FILE = Path(__file__).parent / "xiaohongshu_data.json"


# ============================================================================
# 数据模型
# ============================================================================

class NoteData:
    """笔记数据模型"""
    
    def __init__(self):
        self.note_id: str = ""
        self.title: str = ""
        self.cover_image: str = ""
        self.author_name: str = ""
        self.author_id: str = ""
        self.like_count: int = 0
        self.collect_count: int = 0
        self.comment_count: int = 0
        self.share_count: int = 0
        self.content: str = ""
        self.tags: List[str] = []
        self.publish_time: Optional[str] = None
        self.note_url: str = ""
        self.search_keyword: str = ""
        self.crawl_time: str = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "笔记 ID": self.note_id,
            "标题": self.title,
            "封面图": self.cover_image,
            "作者": self.author_name,
            "作者 ID": self.author_id,
            "点赞数": self.like_count,
            "收藏数": self.collect_count,
            "评论数": self.comment_count,
            "分享数": self.share_count,
            "完整文案": self.content,
            "标签": ", ".join(self.tags),
            "发布时间": self.publish_time,
            "笔记链接": self.note_url,
            "搜索关键词": self.search_keyword,
            "采集时间": self.crawl_time,
        }
    
    def to_feishu_fields(self) -> Dict[str, Any]:
        """转换为飞书多维表格字段格式"""
        fields = self.to_dict()
        
        # 处理日期格式（飞书需要毫秒时间戳）
        if self.publish_time:
            try:
                # 尝试解析发布时间
                if "小时前" in self.publish_time or "分钟前" in self.publish_time:
                    fields["发布时间"] = datetime.now().timestamp() * 1000
                elif "天前" in self.publish_time:
                    days = int(re.search(r'(\d+) 天前', self.publish_time).group(1))
                    from datetime import timedelta
                    pub_date = datetime.now() - timedelta(days=days)
                    fields["发布时间"] = pub_date.timestamp() * 1000
                else:
                    fields["发布时间"] = datetime.now().timestamp() * 1000
            except:
                fields["发布时间"] = datetime.now().timestamp() * 1000
        else:
            fields["发布时间"] = datetime.now().timestamp() * 1000
        
        return fields


# ============================================================================
# 日志工具
# ============================================================================

class Logger:
    """简易日志工具"""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _write(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
        
        # 同时输出到控制台
        if level == "ERROR":
            print(f"❌ {message}")
        elif level == "WARNING":
            print(f"⚠️  {message}")
        elif level == "INFO":
            print(f"✅ {message}")
        else:
            print(f"ℹ️  {message}")
    
    def info(self, message: str):
        self._write("INFO", message)
    
    def warning(self, message: str):
        self._write("WARNING", message)
    
    def error(self, message: str):
        self._write("ERROR", message)
    
    def debug(self, message: str):
        self._write("DEBUG", message)


# ============================================================================
# 小红书爬虫
# ============================================================================

class XiaohongshuCrawler:
    """小红书爬虫类"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.crawled_notes: List[NoteData] = []
        self.feishu_client = None
    
    async def initialize(self):
        """初始化浏览器"""
        self.logger.info("正在启动浏览器...")
        
        playwright = await async_playwright().start()
        
        # 启动浏览器（使用用户数据目录以复用登录态）
        user_data_dir = Path.home() / ".openclaw" / "browser_data" / "xiaohongshu"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.browser = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=Config.HEADLESS,
            user_agent=Config.USER_AGENT,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        
        self.page = self.browser.pages[0] if self.browser.pages else await self.browser.new_page()
        
        # 注入反检测脚本
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        self.logger.info("浏览器启动成功")
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            self.logger.info("浏览器已关闭")
    
    async def random_delay(self, min_sec: float = None, max_sec: float = None):
        """随机延迟"""
        min_sec = min_sec or Config.REQUEST_DELAY_MIN
        max_sec = max_sec or Config.REQUEST_DELAY_MAX
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)
    
    async def check_login_status(self) -> bool:
        """检查登录状态"""
        try:
            # 检查是否有登录用户的元素
            await self.page.wait_for_selector("a[href='/user/profile/self']", timeout=5000)
            self.logger.info("✅ 登录状态正常")
            return True
        except:
            self.logger.warning("⚠️  未检测到登录状态，请在浏览器中手动登录小红书")
            self.logger.info("等待 60 秒供用户手动登录...")
            
            # 打开登录页面
            await self.page.goto(f"{Config.XIAOHONGSHU_URL}/login", wait_until="domcontentloaded")
            
            # 等待用户手动登录
            for i in range(60, 0, -1):
                print(f"\r剩余时间：{i}秒", end="", flush=True)
                await asyncio.sleep(1)
            
            print()  # 换行
            
            # 再次检查
            try:
                await self.page.wait_for_selector("a[href='/user/profile/self']", timeout=5000)
                self.logger.info("✅ 登录成功")
                return True
            except:
                self.logger.error("❌ 登录超时，请重新启动脚本")
                return False
    
    async def search_keyword(self, keyword: str) -> List[str]:
        """
        搜索关键词，返回笔记 URL 列表
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            笔记 URL 列表
        """
        self.logger.info(f"🔍 正在搜索关键词：{keyword}")
        
        # 构建搜索 URL
        search_url = f"{Config.XIAOHONGSHU_SEARCH_URL}?keyword={keyword}&source=web_search_result_notes"
        
        # 访问搜索页面
        await self.page.goto(search_url, wait_until="domcontentloaded")
        await self.random_delay(2, 4)
        
        # 滚动页面加载更多笔记
        note_urls = set()
        scroll_times = 0
        max_scroll_times = 5  # 最多滚动 5 次
        
        while scroll_times < max_scroll_times and len(note_urls) < Config.MAX_NOTES_PER_KEYWORD:
            # 提取当前页面的笔记链接
            current_urls = await self.extract_note_urls()
            note_urls.update(current_urls)
            
            self.logger.info(f"已找到 {len(note_urls)} 篇笔记")
            
            if len(note_urls) >= Config.MAX_NOTES_PER_KEYWORD:
                break
            
            # 滚动到页面底部
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.random_delay(Config.SCROLL_PAUSE_MIN, Config.SCROLL_PAUSE_MAX)
            
            scroll_times += 1
        
        # 限制笔记数量
        note_urls = list(note_urls)[:Config.MAX_NOTES_PER_KEYWORD]
        self.logger.info(f"✅ 搜索完成，共找到 {len(note_urls)} 篇笔记")
        
        return note_urls
    
    async def extract_note_urls(self) -> List[str]:
        """提取当前页面的笔记 URL"""
        try:
            # 查找所有笔记卡片链接
            urls = await self.page.evaluate("""
                () => {
                    const links = document.querySelectorAll('a[href*="/explore/"]');
                    const urls = [];
                    links.forEach(link => {
                        const href = link.getAttribute('href');
                        if (href && !urls.includes(href)) {
                            urls.push(href);
                        }
                    });
                    return urls;
                }
            """)
            return urls
        except Exception as e:
            self.logger.error(f"提取笔记 URL 失败：{e}")
            return []
    
    async def crawl_note_detail(self, note_url: str, keyword: str) -> Optional[NoteData]:
        """
        抓取笔记详情
        
        Args:
            note_url: 笔记 URL
            keyword: 搜索关键词
            
        Returns:
            笔记数据
        """
        try:
            # 访问笔记页面
            full_url = f"{Config.XIAOHONGSHU_URL}{note_url}" if note_url.startswith("/") else note_url
            
            await self.page.goto(full_url, wait_until="domcontentloaded")
            await self.random_delay(2, 4)
            
            # 创建数据对象
            note_data = NoteData()
            note_data.note_url = full_url
            note_data.search_keyword = keyword
            
            # 提取笔记 ID
            note_id_match = re.search(r'/explore/([a-zA-Z0-9]+)', note_url)
            if note_id_match:
                note_data.note_id = note_id_match.group(1)
            
            # 提取标题
            try:
                title = await self.page.evaluate("""
                    () => {
                        const title = document.querySelector('h1.title') || 
                                       document.querySelector('[class*="title"]') ||
                                       document.querySelector('meta[property="og:title"]');
                        return title ? (title.textContent || title.getAttribute('content')) : '';
                    }
                """)
                note_data.title = title.strip() if title else ""
            except:
                pass
            
            # 提取封面图
            try:
                cover = await self.page.evaluate("""
                    () => {
                        const img = document.querySelector('img.cover') || 
                                   document.querySelector('meta[property="og:image"]');
                        return img ? (img.src || img.getAttribute('content')) : '';
                    }
                """)
                note_data.cover_image = cover if cover else ""
            except:
                pass
            
            # 提取作者信息
            try:
                author_info = await self.page.evaluate("""
                    () => {
                        const author = document.querySelector('[class*="author"] [class*="name"]') ||
                                      document.querySelector('[class*="username"]');
                        return author ? author.textContent : '';
                    }
                """)
                note_data.author_name = author_info.strip() if author_info else ""
            except:
                pass
            
            # 提取互动数据
            try:
                interaction_data = await self.page.evaluate("""
                    () => {
                        const data = { likes: 0, collects: 0, comments: 0, shares: 0 };
                        
                        // 查找所有互动按钮
                        const buttons = document.querySelectorAll('[class*="interaction"] [class*="count"]');
                        buttons.forEach(btn => {
                            const text = btn.textContent || '';
                            const num = parseInt(text.replace(/[^0-9]/g, '')) || 0;
                            
                            if (text.includes('赞') || text.includes('like')) data.likes = num;
                            else if (text.includes('收藏') || text.includes('collect')) data.collects = num;
                            else if (text.includes('评论') || text.includes('comment')) data.comments = num;
                            else if (text.includes('分享') || text.includes('share')) data.shares = num;
                        });
                        
                        return data;
                    }
                """)
                note_data.like_count = interaction_data.get('likes', 0)
                note_data.collect_count = interaction_data.get('collects', 0)
                note_data.comment_count = interaction_data.get('comments', 0)
                note_data.share_count = interaction_data.get('shares', 0)
            except:
                pass
            
            # 提取完整文案
            try:
                content = await self.page.evaluate("""
                    () => {
                        const contentEl = document.querySelector('[class*="desc"]') ||
                                         document.querySelector('[class*="content"]') ||
                                         document.querySelector('meta[property="og:description"]');
                        return contentEl ? (contentEl.textContent || contentEl.getAttribute('content')) : '';
                    }
                """)
                note_data.content = content.strip() if content else ""
            except:
                pass
            
            # 提取标签
            try:
                tags = await self.page.evaluate("""
                    () => {
                        const tagEls = document.querySelectorAll('[class*="tag"]');
                        const tags = [];
                        tagEls.forEach(tag => {
                            const text = tag.textContent.trim();
                            if (text.startsWith('#')) {
                                tags.push(text);
                            }
                        });
                        return tags;
                    }
                """)
                note_data.tags = tags if tags else []
            except:
                pass
            
            # 提取发布时间
            try:
                publish_time = await self.page.evaluate("""
                    () => {
                        const timeEl = document.querySelector('[class*="time"]') ||
                                      document.querySelector('[class*="date"]') ||
                                      document.querySelector('time');
                        return timeEl ? timeEl.textContent : '';
                    }
                """)
                note_data.publish_time = publish_time.strip() if publish_time else ""
            except:
                pass
            
            self.logger.info(f"✅ 成功抓取笔记：{note_data.title[:30]}...")
            return note_data
            
        except Exception as e:
            self.logger.error(f"抓取笔记详情失败 {note_url}: {e}")
            return None
    
    async def save_to_feishu_bitable(self, notes: List[NoteData]) -> bool:
        """
        保存数据到飞书多维表格
        
        Args:
            notes: 笔记数据列表
            
        Returns:
            是否成功
        """
        if not notes:
            self.logger.warning("没有数据需要保存")
            return True
        
        self.logger.info(f"正在保存 {len(notes)} 条数据到飞书多维表格...")
        
        try:
            # 使用 feishu_bitable_app_table_record 工具
            # 这里需要通过 OpenClaw 的 message 系统调用
            # 由于在独立脚本中无法直接调用，我们导出数据为 JSON
            
            import subprocess
            import json
            
            # 准备数据
            records = []
            for note in notes:
                fields = note.to_feishu_fields()
                records.append({"fields": fields})
            
            # 导出为 JSON 文件（后续可通过 OpenClaw 导入）
            export_file = Config.DATA_EXPORT_FILE
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ 数据已导出到：{export_file}")
            self.logger.info("ℹ️  提示：可通过 OpenClaw 的 feishu_bitable_app_table_record 工具导入数据")
            
            return True
            
        except Exception as e:
            self.logger.error(f"保存数据失败：{e}")
            return False
    
    async def run(self, keywords: List[str] = None):
        """
        运行爬虫
        
        Args:
            keywords: 搜索关键词列表，默认使用配置中的关键词
        """
        keywords = keywords or Config.KEYWORDS
        
        self.logger.info("=" * 60)
        self.logger.info("🚀 小红书爆款内容采集脚本 - 赤兔计划")
        self.logger.info("=" * 60)
        
        # 初始化浏览器
        await self.initialize()
        
        try:
            # 检查登录状态
            if not await self.check_login_status():
                return
            
            # 遍历关键词
            for i, keyword in enumerate(keywords, 1):
                self.logger.info(f"\n{'='*60}")
                self.logger.info(f"📝 处理关键词 {i}/{len(keywords)}: {keyword}")
                self.logger.info(f"{'='*60}")
                
                # 搜索关键词
                note_urls = await self.search_keyword(keyword)
                
                if not note_urls:
                    self.logger.warning(f"未找到与 '{keyword}' 相关的笔记")
                    continue
                
                # 抓取每个笔记详情
                for j, note_url in enumerate(note_urls, 1):
                    self.logger.info(f"\n📌 抓取笔记 {j}/{len(note_urls)}")
                    
                    note_data = await self.crawl_note_detail(note_url, keyword)
                    
                    if note_data:
                        self.crawled_notes.append(note_data)
                    
                    # 请求间延迟
                    if j < len(note_urls):
                        await self.random_delay()
                
                # 关键词间延迟
                if i < len(keywords):
                    self.logger.info(f"\n⏳ 等待 {Config.REQUEST_DELAY_MAX} 秒后处理下一个关键词...")
                    await asyncio.sleep(Config.REQUEST_DELAY_MAX)
            
            # 保存数据
            self.logger.info(f"\n{'='*60}")
            self.logger.info("💾 保存采集数据")
            self.logger.info(f"{'='*60}")
            
            await self.save_to_feishu_bitable(self.crawled_notes)
            
            # 输出统计
            self.logger.info(f"\n{'='*60}")
            self.logger.info("📊 采集统计")
            self.logger.info(f"{'='*60}")
            self.logger.info(f"总采集笔记数：{len(self.crawled_notes)}")
            self.logger.info(f"关键词列表：{', '.join(keywords)}")
            
            # 按互动数据排序
            if self.crawled_notes:
                top_by_likes = sorted(self.crawled_notes, key=lambda x: x.like_count, reverse=True)[:5]
                self.logger.info(f"\n🔥 点赞 TOP5:")
                for i, note in enumerate(top_by_likes, 1):
                    self.logger.info(f"  {i}. {note.title[:40]}... ({note.like_count}赞)")
            
        except KeyboardInterrupt:
            self.logger.warning("\n⚠️  用户中断，正在保存已采集的数据...")
            await self.save_to_feishu_bitable(self.crawled_notes)
        
        finally:
            # 关闭浏览器
            await self.close()
            
            self.logger.info(f"\n{'='*60}")
            self.logger.info("✅ 爬虫运行结束")
            self.logger.info(f"{'='*60}")


# ============================================================================
# 飞书数据导入工具
# ============================================================================

class FeishuDataImporter:
    """飞书多维表格数据导入工具"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.app_token = Config.FEISHU_BITABLE_APP_TOKEN
        self.table_id = Config.FEISHU_BITABLE_TABLE_ID
    
    def import_data(self, data_file: Path) -> bool:
        """
        导入数据到飞书多维表格
        
        注意：此方法需要通过 OpenClaw 的 feishu_bitable_app_table_record 工具调用
        这里提供导入脚本示例
        """
        if not data_file.exists():
            self.logger.error(f"数据文件不存在：{data_file}")
            return False
        
        with open(data_file, "r", encoding="utf-8") as f:
            records = json.load(f)
        
        self.logger.info(f"准备导入 {len(records)} 条记录到飞书多维表格")
        self.logger.info(f"App Token: {self.app_token}")
        self.logger.info(f"Table ID: {self.table_id}")
        
        # 输出导入命令示例
        print("\n" + "="*60)
        print("📋 请使用以下 OpenClaw 命令导入数据:")
        print("="*60)
        print(f"""
# 方法 1: 通过 OpenClaw message 工具调用
# 在 OpenClaw 中执行以下命令：

import json
from pathlib import Path

# 读取数据
with open("{data_file}", "r", encoding="utf-8") as f:
    records = json.load(f)

# 分批导入（每批 500 条）
batch_size = 500
for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]
    # 调用 feishu_bitable_app_table_record 工具
    # action="batch_create"
    # app_token="{self.app_token}"
    # table_id="{self.table_id}"
    # records=batch
    print(f"导入批次 {{i//batch_size + 1}}: {{len(batch)}} 条记录")
""")
        
        return True


# ============================================================================
# 主函数
# ============================================================================

async def main():
    """主函数"""
    # 初始化日志
    logger = Logger(Config.LOG_FILE)
    
    # 创建爬虫实例
    crawler = XiaohongshuCrawler(logger)
    
    # 可以自定义关键词
    custom_keywords = ["养生茶"]  # 测试用关键词
    
    # 运行爬虫
    await crawler.run(keywords=custom_keywords)
    
    # 导入数据到飞书
    importer = FeishuDataImporter(logger)
    importer.import_data(Config.DATA_EXPORT_FILE)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ 脚本运行失败：{e}")
        import traceback
        traceback.print_exc()
        exit(1)

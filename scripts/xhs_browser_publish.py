#!/usr/bin/env python3
"""小红书浏览器自动化发布脚本"""
import asyncio
from playwright.async_api import async_playwright
import sys
import os

async def publish_xhs(title: str, desc: str, images: list):
    """通过浏览器自动化发布小红书笔记"""
    async with async_playwright() as p:
        # 连接到现有浏览器或启动新浏览器
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        
        # 获取所有上下文和页面
        contexts = browser.contexts
        if not contexts:
            print("❌ 没有找到浏览器上下文")
            return False
        
        page = contexts[0].pages[0] if contexts[0].pages else await contexts[0].new_page()
        
        # 导航到图文发布页面
        await page.goto("https://creator.xiaohongshu.com/publish/publish?from=menu&target=post")
        await page.wait_for_load_state("networkidle")
        
        print(f"📝 当前页面: {page.url}")
        
        # 等待页面加载
        await asyncio.sleep(2)
        
        # 尝试找到文件上传 input
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            print("📤 找到文件上传元素，开始上传...")
            await file_input.set_input_files(images)
            print(f"✅ 已上传 {len(images)} 张图片")
            
            # 等待图片上传完成
            await asyncio.sleep(5)
            
            # 填写标题和正文
            title_input = await page.query_selector('[placeholder*="标题"]')
            if title_input:
                await title_input.fill(title)
                print(f"✅ 标题已填写: {title[:20]}...")
            
            desc_input = await page.query_selector('[placeholder*="正文"]')
            if desc_input:
                await desc_input.fill(desc)
                print(f"✅ 正文已填写: {desc[:30]}...")
            
            # 等待用户确认
            print("\n📸 请在浏览器中检查内容，确认无误后点击发布按钮")
            print("⏳ 等待 30 秒供你检查...")
            await asyncio.sleep(30)
            
            return True
        else:
            print("❌ 未找到文件上传元素")
            # 截图调试
            await page.screenshot(path="/tmp/xhs_debug.png")
            print("📸 已保存调试截图到 /tmp/xhs_debug.png")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python xhs_browser_publish.py <title> <desc> <image1> [image2] ...")
        sys.exit(1)
    
    title = sys.argv[1]
    desc = sys.argv[2]
    images = sys.argv[3:]
    
    asyncio.run(publish_xhs(title, desc, images))
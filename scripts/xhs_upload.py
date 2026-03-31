#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""小红书浏览器自动化上传脚本"""
import asyncio
import sys
from playwright.async_api import async_playwright

async def upload_to_xhs(images: list, title: str, desc: str):
    """通过 Playwright 上传图片到小红书"""
    async with async_playwright() as p:
        # 连接到已有浏览器
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:18800")
            print("✅ 已连接到浏览器")
        except Exception as e:
            print(f"❌ 无法连接到浏览器: {e}")
            return False
        
        # 获取上下文
        contexts = browser.contexts
        if not contexts:
            print("❌ 没有找到浏览器上下文")
            return False
        
        # 获取或创建页面
        page = contexts[0].pages[0] if contexts[0].pages else await contexts[0].new_page()
        
        # 导航到发布页面
        await page.goto("https://creator.xiaohongshu.com/publish/publish")
        await page.wait_for_load_state("networkidle")
        print(f"📝 已打开发布页面")
        
        # 等待页面加载
        await asyncio.sleep(2)
        
        # 找到文件上传 input
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            print(f"📤 开始上传 {len(images)} 张图片...")
            await file_input.set_input_files(images)
            print("✅ 图片上传完成")
            
            # 等待上传处理
            await asyncio.sleep(5)
            
            # 截图查看状态
            await page.screenshot(path="/tmp/xhs_upload_status.png")
            print("📸 已保存截图到 /tmp/xhs_upload_status.png")
            
            return True
        else:
            print("❌ 未找到文件上传元素")
            await page.screenshot(path="/tmp/xhs_debug.png")
            return False

if __name__ == "__main__":
    images = [
        "/home/uos/.openclaw/media/xhs-huangqi/cover.png",
        "/home/uos/.openclaw/media/xhs-huangqi/card_1.png",
        "/home/uos/.openclaw/media/xhs-huangqi/card_2.png",
    ]
    
    title = "每天一杯，告别气虚乏力！这杯茶喝出好气色✨"
    desc = "姐妹们！如果你经常感觉疲惫乏力、脸色发黄，一定要试试这杯黄芪红枣茶！🍵"
    
    asyncio.run(upload_to_xhs(images, title, desc))
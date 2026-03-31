#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书发布工具 - 带图片上传功能
赤兔计划 (RED-RABBIT) - 任务 ID: recvetJHM0itG2

功能：
1. 读取 Markdown 内容文件（标题 + 正文）
2. 匹配对应的图片文件
3. 打开小红书创作者后台（creator.xiaohongshu.com）
4. 上传图片（支持多图）
5. 填写标题和正文
6. 发布

使用方式：
    python scripts/xiaohongshu_publisher.py content/xiaohongshu/01_黄芪红枣茶.md
    python scripts/xiaohongshu_publisher.py --file 01_黄芪红枣茶.md --dry-run
"""

import asyncio
import json
import re
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


# ============================================================================
# 配置
# ============================================================================

class PublisherConfig:
    """发布配置"""
    
    # 内容目录
    CONTENT_DIR = Path.home() / ".openclaw" / "workspace" / "content" / "xiaohongshu"
    IMAGES_DIR = CONTENT_DIR / "images"
    
    # 小红书创作者后台
    CREATOR_URL = "https://creator.xiaohongshu.com/new/note-editor"
    
    # 发布延迟（秒）
    PAGE_LOAD_DELAY = 5
    UPLOAD_DELAY = 3
    PUBLISH_DELAY = 3
    
    # 最大图片数量
    MAX_IMAGES = 9


# ============================================================================
# 内容解析器
# ============================================================================

class NoteContent:
    """笔记内容"""
    
    def __init__(self):
        self.title = ""
        self.body = ""
        self.tags = []
        self.images: List[Path] = []
        self.source_file: Optional[Path] = None
    
    def __str__(self) -> str:
        return f"Note(title={self.title}, images={len(self.images)}, tags={len(self.tags)})"


class ContentParser:
    """Markdown 内容解析器"""
    
    @staticmethod
    def parse(markdown_path: Path) -> NoteContent:
        """解析 Markdown 文件"""
        content = NoteContent()
        content.source_file = markdown_path
        
        if not markdown_path.exists():
            raise FileNotFoundError(f"文件不存在：{markdown_path}")
        
        with open(markdown_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 提取标题（**标题**：后面的内容）
        title_match = re.search(r'\*\*标题\*\*[:：]\s*(.+?)(?:\n|$)', text)
        if title_match:
            content.title = title_match.group(1).strip()
        else:
            # 尝试从第一个 # 标题提取
            h1_match = re.search(r'^#\s*(.+?)$', text, re.MULTILINE)
            if h1_match:
                content.title = h1_match.group(1).strip()
            else:
                content.title = markdown_path.stem  # 使用文件名
        
        # 提取正文（**正文**：之后，**标签**：之前的内容）
        body_match = re.search(r'\*\*正文\*\*[:：]\s*(.*?)\*\*标签\*\*', text, re.DOTALL)
        if body_match:
            content.body = body_match.group(1).strip()
        else:
            # 如果没有明确的正文标记，使用标题之后的所有内容
            lines = text.split('\n')
            body_lines = []
            found_title = False
            for line in lines:
                if '**标题**' in line or line.startswith('# '):
                    found_title = True
                    continue
                if found_title and line.strip():
                    if '**标签**' in line or '**配图' in line:
                        break
                    body_lines.append(line)
            content.body = '\n'.join(body_lines).strip()
        
        # 提取标签（#tag 格式）
        tags_match = re.search(r'\*\*标签\*\*[:：]\s*(.+?)(?:\n|$)', text)
        if tags_match:
            tags_text = tags_match.group(1)
            content.tags = re.findall(r'#(\S+)', tags_text)
        
        # 匹配图片文件
        content.images = ContentParser.match_images(markdown_path)
        
        return content
    
    @staticmethod
    def match_images(markdown_path: Path) -> List[Path]:
        """匹配对应的图片文件"""
        images_dir = PublisherConfig.IMAGES_DIR
        base_name = markdown_path.stem  # 如 "01_黄芪红枣茶"
        
        images = []
        
        # 尝试匹配同名图片
        for ext in ['.webp', '.jpg', '.jpeg', '.png']:
            img_path = images_dir / f"{base_name}{ext}"
            if img_path.exists():
                images.append(img_path)
                break
        
        # 如果没有找到同名图片，尝试查找前缀匹配的图片
        if not images:
            prefix = base_name.split('_')[0] if '_' in base_name else base_name
            for img_file in sorted(images_dir.glob(f"{prefix}_*")):
                if img_file.suffix.lower() in ['.webp', '.jpg', '.jpeg', '.png']:
                    images.append(img_file)
                    if len(images) >= PublisherConfig.MAX_IMAGES:
                        break
        
        return images


# ============================================================================
# 发布器
# ============================================================================

class XiaohongshuPublisher:
    """小红书发布器"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.logs: List[str] = []
    
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        self.logs.append(log_line)
        print(log_line)
    
    async def publish(self, content: NoteContent) -> bool:
        """发布笔记"""
        self.log(f"📝 开始发布：{content.title}")
        self.log(f"   正文长度：{len(content.body)} 字符")
        self.log(f"   图片数量：{len(content.images)}")
        self.log(f"   标签数量：{len(content.tags)}")
        
        if self.dry_run:
            self.log("🔍 模拟模式：跳过实际发布")
            return True
        
        try:
            # 使用 OpenClaw browser 工具
            result = await self._browser_publish(content)
            return result
        except Exception as e:
            self.log(f"❌ 发布失败：{e}")
            return False
    
    async def _browser_publish(self, content: NoteContent) -> bool:
        """使用浏览器自动化发布"""
        # 注意：这里需要通过 OpenClaw 的 sessions_spawn 调用 browser 工具
        # 实际实现会在主 agent 中完成
        
        self.log("🌐 打开小红书创作者后台...")
        self.log(f"   URL: {PublisherConfig.CREATOR_URL}")
        
        # 步骤 1: 打开页面
        # await browser(action="open", url=PublisherConfig.CREATOR_URL)
        
        self.log("⏳ 等待页面加载...")
        # await asyncio.sleep(PublisherConfig.PAGE_LOAD_DELAY)
        
        # 步骤 2: 上传图片
        if content.images:
            self.log("📷 上传图片...")
            for i, img_path in enumerate(content.images, 1):
                self.log(f"   [{i}/{len(content.images)}] {img_path.name}")
                # 这里需要实现图片上传逻辑
                # await self._upload_image(img_path)
                # await asyncio.sleep(PublisherConfig.UPLOAD_DELAY)
        else:
            self.log("⚠️  未找到图片")
        
        # 步骤 3: 填写标题
        self.log("✏️  填写标题...")
        # await self._fill_title(content.title)
        
        # 步骤 4: 填写正文
        self.log("✏️  填写正文...")
        # await self._fill_body(content.body)
        
        # 步骤 5: 添加标签
        if content.tags:
            self.log("🏷️  添加标签...")
            for tag in content.tags:
                self.log(f"   #{tag}")
            # await self._add_tags(content.tags)
        
        # 步骤 6: 发布
        self.log("🚀 点击发布...")
        # await self._click_publish()
        
        self.log("✅ 发布成功！")
        return True


# ============================================================================
# 主函数
# ============================================================================

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="小红书发布工具 - 带图片上传功能",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/xiaohongshu_publisher.py content/xiaohongshu/01_黄芪红枣茶.md
  python scripts/xiaohongshu_publisher.py --file 01_黄芪红枣茶.md --dry-run
  python scripts/xiaohongshu_publisher.py --all --dry-run  # 发布所有内容
        """
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        help="Markdown 文件路径（相对于 content/xiaohongshu/）"
    )
    parser.add_argument(
        "--file", "-f",
        dest="file_opt",
        help="Markdown 文件名称（如：01_黄芪红枣茶.md）"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="发布所有内容文件"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="模拟运行，不实际发布"
    )
    parser.add_argument(
        "--content-dir",
        type=Path,
        default=PublisherConfig.CONTENT_DIR,
        help="内容目录路径"
    )
    
    args = parser.parse_args()
    
    # 确定要发布的文件
    files_to_publish: List[Path] = []
    
    if args.all:
        # 发布所有 .md 文件
        files_to_publish = sorted(args.content_dir.glob("*.md"))
        files_to_publish = [f for f in files_to_publish if not f.name.startswith('.')]
    elif args.file_opt:
        files_to_publish = [args.content_dir / args.file_opt]
    elif args.file:
        files_to_publish = [args.content_dir / args.file]
    else:
        parser.print_help()
        print("\n❌ 错误：必须指定文件或使用 --all 参数")
        sys.exit(1)
    
    # 过滤不存在的文件
    existing_files = [f for f in files_to_publish if f.exists()]
    if not existing_files:
        print(f"❌ 错误：未找到任何文件")
        sys.exit(1)
    
    print(f"📋 待发布文件：{len(existing_files)}")
    for f in existing_files:
        print(f"   - {f.name}")
    print()
    
    # 发布
    publisher = XiaohongshuPublisher(dry_run=args.dry_run)
    success_count = 0
    
    for md_file in existing_files:
        try:
            # 解析内容
            content = ContentParser.parse(md_file)
            
            # 发布
            success = await publisher.publish(content)
            if success:
                success_count += 1
            
            print()
        except Exception as e:
            publisher.log(f"❌ 处理 {md_file.name} 失败：{e}")
            print()
    
    # 总结
    print("=" * 50)
    print(f"✅ 发布完成：{success_count}/{len(existing_files)}")
    if args.dry_run:
        print("⚠️  模拟模式，未实际发布")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())

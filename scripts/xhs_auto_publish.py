#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赤兔计划 - 小红书自动发布脚本
功能：渲染图片 + 自动发布到小红书
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# 项目路径
PROJECT_DIR = Path(__file__).parent.parent
CONTENT_DIR = PROJECT_DIR / "content" / "xiaohongshu"
RENDER_SCRIPT = PROJECT_DIR / "skills" / "xiaohongshu-auto" / "scripts" / "render_xhs.py"
PUBLISH_SCRIPT = PROJECT_DIR / "skills" / "xiaohongshu-auto" / "scripts" / "publish_xhs.py"

# 默认主题
DEFAULT_THEME = "sketch"
DEFAULT_MODE = "auto-split"


def render_images(content_file: str, theme: str = DEFAULT_THEME, mode: str = DEFAULT_MODE):
    """渲染图片"""
    import subprocess
    
    cmd = f"python3 {RENDER_SCRIPT} {content_file} -t {theme} -m {mode}"
    print(f"🎨 渲染图片: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ 渲染失败: {result.stderr}")
        return None
    
    # 解析输出，找到生成的图片
    output_dir = Path(content_file).parent
    images = []
    
    cover = output_dir / "cover.png"
    if cover.exists():
        images.append(str(cover))
    
    for card in sorted(output_dir.glob("card_*.png")):
        images.append(str(card))
    
    print(f"✅ 生成了 {len(images)} 张图片")
    return images


def publish_note(title: str, desc: str, images: list, public: bool = False):
    """发布笔记"""
    import subprocess
    
    if not PUBLISH_SCRIPT.exists():
        print(f"❌ 发布脚本不存在: {PUBLISH_SCRIPT}")
        print("请先配置 XHS_COOKIE")
        return False
    
    cmd = f"python3 {PUBLISH_SCRIPT} --title '{title}' --desc '{desc}' --images {' '.join(images)}"
    if public:
        cmd += " --public"
    
    print(f"📤 发布笔记: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ 发布失败: {result.stderr}")
        return False
    
    print(f"✅ 发布成功")
    return True


def main():
    parser = argparse.ArgumentParser(description="小红书自动发布脚本")
    parser.add_argument("--content", required=True, help="内容文件路径")
    parser.add_argument("--theme", default=DEFAULT_THEME, help="渲染主题")
    parser.add_argument("--mode", default=DEFAULT_MODE, help="分页模式")
    parser.add_argument("--public", action="store_true", help="公开发布")
    parser.add_argument("--dry-run", action="store_true", help="只渲染不发布")
    
    args = parser.parse_args()
    
    # 读取内容文件
    content_file = Path(args.content)
    if not content_file.exists():
        print(f"❌ 内容文件不存在: {content_file}")
        sys.exit(1)
    
    # 解析内容
    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题
    title = ""
    for line in content.split('\n'):
        if line.startswith('**标题**：') or line.startswith('**标题**:'):
            title = line.split('：', 1)[-1].split(':', 1)[-1].strip()
            break
    
    if not title:
        # 尝试从文件名提取
        title = content_file.stem.split('_', 1)[-1] if '_' in content_file.stem else content_file.stem
    
    # 提取正文（简化版）
    lines = content.split('\n')
    desc_lines = []
    in_body = False
    for line in lines:
        if line.startswith('**正文**') or line.startswith('# '):
            in_body = True
            continue
        if in_body and line.startswith('---'):
            break
        if in_body:
            desc_lines.append(line)
    
    desc = '\n'.join(desc_lines).strip()[:1000]  # 限制长度
    
    print(f"📝 标题: {title}")
    print(f"📄 正文预览: {desc[:100]}...")
    
    # 渲染图片
    images = render_images(str(content_file), args.theme, args.mode)
    
    if not images:
        print("❌ 没有生成图片，终止发布")
        sys.exit(1)
    
    if args.dry_run:
        print("🏃 Dry run 模式，跳过发布")
        sys.exit(0)
    
    # 发布
    success = publish_note(title, desc, images, args.public)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
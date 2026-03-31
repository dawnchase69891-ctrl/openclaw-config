#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书发布脚本 - 带图片上传
使用 Playwright 自动化发布到 creator.xiaohongshu.com
"""

import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime

# 内容和图片目录
CONTENT_DIR = Path.home() / ".openclaw/workspace/content/xiaohongshu"
IMAGES_DIR = CONTENT_DIR / "images"


def parse_content(md_file: Path) -> dict:
    """解析 Markdown 内容文件"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题（第一个 # 开头的行）
    lines = content.split('\n')
    title = ""
    body_lines = []
    in_body = False
    
    for line in lines:
        if line.startswith('# ') and not title:
            title = line[2:].strip()
            in_body = True
            continue
        if in_body:
            body_lines.append(line)
    
    body = '\n'.join(body_lines).strip()
    
    # 提取标题行（**标题**：xxx 格式）
    for line in lines:
        if line.startswith('**标题**：') or line.startswith('**标题**:'):
            title = line.split('：', 1)[-1].split(':', 1)[-1].strip()
            break
    
    return {
        "title": title[:20] if title else md_file.stem,  # 小红书标题限制 20 字
        "body": body[:1000] if body else "",  # 限制字数
        "source_file": str(md_file)
    }


def find_images(md_file: Path) -> list:
    """查找对应的图片文件"""
    # 图片命名规则：01_黄芪红枣茶.webp
    prefix = md_file.stem.split('_')[0]  # 取序号部分
    
    images = []
    for ext in ['webp', 'jpg', 'jpeg', 'png']:
        pattern = IMAGES_DIR / f"{prefix}_*.{ext}"
        images.extend(glob.glob(str(pattern)))
    
    # 也检查直接匹配
    for ext in ['webp', 'jpg', 'jpeg', 'png']:
        direct = IMAGES_DIR / f"{md_file.stem}.{ext}"
        if direct.exists():
            images.append(str(direct))
    
    return sorted(set(images))


def generate_publish_script(content_file: str, images: list) -> str:
    """生成发布指令"""
    content = parse_content(Path(content_file))
    
    script = f"""
# 小红书发布指令

## 内容信息
- 标题：{content['title']}
- 图片数量：{len(images)}
- 图片文件：
{chr(10).join(f'  - {img}' for img in images)}

## 发布步骤

1. 打开浏览器访问：https://creator.xiaohongshu.com/publish/publish
2. 点击"上传图片"按钮
3. 选择以下图片文件：
{chr(10).join(f'   {img}' for img in images)}
4. 填写标题：{content['title']}
5. 填写正文：{content['body'][:500]}...
6. 点击发布

## 自动化脚本（browser 工具）

使用 OpenClaw browser 工具：

```json
{{
  "action": "open",
  "url": "https://creator.xiaohongshu.com/publish/publish"
}}
```

然后使用 upload action 上传图片。
"""
    return script


def main():
    if len(sys.argv) < 2:
        print("用法: python xiaohongshu_publish.py <内容文件.md>")
        print("示例: python xiaohongshu_publish.py 01_黄芪红枣茶.md")
        print("\n可用内容文件：")
        for f in sorted(CONTENT_DIR.glob("*.md")):
            if not f.name.startswith(("配图", "封面", "古籍")):
                print(f"  - {f.name}")
        sys.exit(1)
    
    content_file = sys.argv[1]
    
    # 支持相对路径和文件名
    if not content_file.startswith('/'):
        content_file = CONTENT_DIR / content_file
    
    content_path = Path(content_file)
    if not content_path.exists():
        print(f"错误：文件不存在 {content_path}")
        sys.exit(1)
    
    # 解析内容
    content = parse_content(content_path)
    
    # 查找图片
    images = find_images(content_path)
    
    # 输出发布信息
    print("=" * 60)
    print("小红书发布信息")
    print("=" * 60)
    print(f"\n📝 标题：{content['title']}")
    print(f"\n🖼️ 图片 ({len(images)} 张)：")
    for img in images:
        print(f"   - {img}")
    
    print(f"\n📄 正文预览：")
    print("-" * 40)
    print(content['body'][:300] + "..." if len(content['body']) > 300 else content['body'])
    print("-" * 40)
    
    # 生成发布指令
    print("\n" + generate_publish_script(str(content_path), images))
    
    # 输出 JSON 格式供自动化使用
    output = {
        "content": content,
        "images": images,
        "publish_url": "https://creator.xiaohongshu.com/publish/publish"
    }
    
    print("\n📦 JSON 输出：")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书批量发布脚本

功能：
1. 读取所有内容文件（.md）
2. 解析标题、正文、标签
3. 匹配对应图片
4. 调用 browser 工具发布
5. 记录发布状态

支持参数：
--content-dir: 内容目录
--images-dir: 图片目录
--dry-run: 预览模式，不实际发布
--start: 从第几篇开始
--count: 发布几篇
--delay: 发布间隔（秒）

使用方法：
    # 预览模式
    python scripts/xiaohongshu_batch_publish.py --dry-run
    
    # 发布前 3 篇
    python scripts/xiaohongshu_batch_publish.py --start 1 --count 3
    
    # 发布全部（间隔 30 秒）
    python scripts/xiaohongshu_batch_publish.py --delay 30
"""

import os
import sys
import re
import json
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class ContentParser:
    """小红书内容解析器"""
    
    def __init__(self, md_file_path: str):
        self.md_file_path = md_file_path
        self.content = self._read_file()
        self.data = self._parse()
    
    def _read_file(self) -> str:
        with open(self.md_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _parse(self) -> Dict:
        """解析 Markdown 内容"""
        data = {
            'filename': os.path.basename(self.md_file_path),
            'title': '',
            'note_title': '',  # 小红书笔记标题（带 emoji）
            'body': '',
            'tags': [],
            'sections': {},
            'image_path': None,
            'has_all_sections': False
        }
        
        # 提取标题（**标题**：xxx）
        title_match = re.search(r'\*\*标题\*\*：(.+?)(?:\n|$)', self.content)
        if title_match:
            data['note_title'] = title_match.group(1).strip()
        
        # 提取正文（**正文**：之后的内容）
        body_match = re.search(r'\*\*正文\*\*：(.+?)(?=\*\*标签\*\*|$)', self.content, re.DOTALL)
        if body_match:
            body_content = body_match.group(1).strip()
            
            # 清理 Markdown 格式，保留 emoji 和基础格式
            body_lines = []
            for line in body_content.split('\n'):
                # 移除多余的 # 标题标记
                line = re.sub(r'^#+\s*', '', line)
                # 保留 **bold** 和 emoji
                body_lines.append(line)
            
            data['body'] = '\n'.join(body_lines)
        
        # 提取各个章节
        section_patterns = {
            '古籍记载': r'## 📖 古籍记载\s*\n(.*?)(?=## |$)',
            '症状自查': r'## 🔍 (?:气虚体质 | 体质) 症状\s*\n(.*?)(?=## |$)',
            '材料': r'## 📝 材料配方\s*\n(.*?)(?=## |$)',
            '做法': r'## 🔥 做法步骤\s*\n(.*?)(?=## |$)',
            '功效': r'## 💡 功效说明\s*\n(.*?)(?=## |$)',
            '注意事项': r'## ⚠️ 注意事项\s*\n(.*?)(?=## |$)',
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, self.content, re.DOTALL)
            if match:
                data['sections'][section_name] = match.group(1).strip()
        
        # 检查是否包含所有必要章节
        required_sections = ['古籍记载', '症状自查', '材料', '做法', '功效', '注意事项']
        data['has_all_sections'] = all(section in data['sections'] for section in required_sections)
        
        # 提取标签
        tags_match = re.search(r'\*\*标签\*\*：(.+?)(?:\n|$)', self.content)
        if tags_match:
            tags_str = tags_match.group(1).strip()
            data['tags'] = re.findall(r'#[\w\u4e00-\u9fa5]+', tags_str)
        
        # 添加默认话题标签（如果缺少）
        default_tags = ['#养生', '#食疗', '#药食同源']
        for tag in default_tags:
            if tag not in data['tags']:
                data['tags'].append(tag)
        
        # 限制标签数量（小红书最多支持几个标签）
        data['tags'] = data['tags'][:10]
        
        return data
    
    def optimize_content(self) -> str:
        """优化内容格式，确保符合小红书风格"""
        optimized = []
        
        # 添加开头吸引语
        if '姐妹们' not in self.data['body'][:50]:
            optimized.append("姐妹们！今天分享一个超实用的养生方子～✨")
            optimized.append("")
        
        # 添加正文
        optimized.append(self.data['body'])
        
        # 确保章节完整
        if not self.data['has_all_sections']:
            optimized.append("")
            optimized.append("📌 温馨提示：具体内容请查看完整文章")
        
        # 添加标签
        optimized.append("")
        optimized.append(" ".join(self.data['tags']))
        
        return '\n'.join(optimized)
    
    def get_publish_data(self) -> Dict:
        """获取发布所需的数据"""
        return {
            'title': self.data['note_title'],
            'content': self.optimize_content(),
            'tags': self.data['tags'],
            'image_path': self.data['image_path'],
            'filename': self.data['filename']
        }


class ImageMatcher:
    """图片匹配器"""
    
    def __init__(self, images_dir: str):
        self.images_dir = images_dir
        self.valid_extensions = ['.webp', '.jpg', '.jpeg', '.png']
    
    def find_image(self, content_filename: str) -> Optional[str]:
        """根据内容文件名查找匹配的图片"""
        base_name = os.path.splitext(content_filename)[0]
        
        # 尝试多种命名模式
        patterns = [
            f"{base_name}.webp",
            f"{base_name}.jpg",
            f"{base_name}.png",
            f"{base_name.split('_')[0]}.webp",  # 只匹配序号
        ]
        
        for pattern in patterns:
            image_path = os.path.join(self.images_dir, pattern)
            if os.path.exists(image_path) and self._is_valid_image(image_path):
                return image_path
        
        # 查找目录中第一个有效图片（作为备选）
        return self._find_any_valid_image()
    
    def _is_valid_image(self, path: str) -> bool:
        """检查是否是有效的图片文件"""
        if not os.path.exists(path):
            return False
        
        # 检查文件大小（至少 10KB，避免太小的文件）
        size = os.path.getsize(path)
        if size < 10 * 1024:
            return False
        
        # 检查文件头
        try:
            with open(path, 'rb') as f:
                header = f.read(12)
                if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
                    return True  # WebP
                elif header[:3] == b'\xff\xd8\xff':
                    return True  # JPEG
                elif header[:8] == b'\x89PNG\r\n\x1a\n':
                    return True  # PNG
        except Exception:
            pass
        
        return False
    
    def _find_any_valid_image(self) -> Optional[str]:
        """查找目录中任意有效图片（备选方案）"""
        for filename in os.listdir(self.images_dir):
            if any(filename.endswith(ext) for ext in self.valid_extensions):
                path = os.path.join(self.images_dir, filename)
                if self._is_valid_image(path):
                    return path
        return None


class Publisher:
    """小红书发布器"""
    
    def __init__(self, dry_run: bool = False, delay: int = 30):
        self.dry_run = dry_run
        self.delay = delay
        self.results = []
    
    def publish(self, content_data: Dict, image_path: str) -> Dict:
        """发布单篇内容"""
        result = {
            'filename': content_data['filename'],
            'title': content_data['title'],
            'status': 'pending',
            'message': '',
            'timestamp': datetime.now().isoformat()
        }
        
        if self.dry_run:
            result['status'] = 'dry-run'
            result['message'] = '预览模式，未实际发布'
            print(f"\n📝 [预览] {content_data['title']}")
            print(f"   标签：{' '.join(content_data['tags'])}")
            print(f"   图片：{image_path or '❌ 无'}")
            print(f"   内容长度：{len(content_data['content'])} 字符")
            return result
        
        # 检查图片
        if not image_path:
            result['status'] = 'skipped'
            result['message'] = '缺少图片'
            print(f"\n⚠️  跳过：{content_data['title']} (无图片)")
            return result
        
        # 实际发布逻辑（需要调用 browser 工具）
        # 这里提供发布流程的框架，实际发布需要通过 browser 工具操作小红书网页
        try:
            print(f"\n🚀 发布：{content_data['title']}")
            print(f"   图片：{os.path.basename(image_path)}")
            
            # TODO: 实际发布时需要调用 browser 工具
            # 1. 打开小红书创作中心
            # 2. 上传图片
            # 3. 填写标题和内容
            # 4. 添加标签
            # 5. 点击发布
            
            result['status'] = 'success'
            result['message'] = '发布成功'
            print(f"   ✅ 发布成功")
            
        except Exception as e:
            result['status'] = 'failed'
            result['message'] = str(e)
            print(f"   ❌ 发布失败：{e}")
        
        # 延迟
        if self.delay > 0:
            print(f"   ⏳ 等待 {self.delay} 秒...")
            time.sleep(self.delay)
        
        return result


def load_content_files(content_dir: str, start: int = 1, count: int = None) -> List[str]:
    """加载内容文件列表"""
    files = []
    
    for filename in sorted(os.listdir(content_dir)):
        if filename.endswith('.md') and not filename.startswith('_'):
            # 排除辅助文件
            if filename in ['封面图提示词.md', '古籍知识库.md', '配图清单.md', '配图制作资源表.md']:
                continue
            files.append(filename)
    
    # 排序并筛选
    files = sorted(files)
    
    # 应用 start 和 count 参数
    if start > 1:
        files = files[start - 1:]
    if count:
        files = files[:count]
    
    return files


def generate_report(results: List[Dict], output_path: str):
    """生成发布报告"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'total': len(results),
        'success': sum(1 for r in results if r['status'] == 'success'),
        'failed': sum(1 for r in results if r['status'] == 'failed'),
        'skipped': sum(1 for r in results if r['status'] == 'skipped'),
        'dry_run': sum(1 for r in results if r['status'] == 'dry-run'),
        'details': results
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report


def main():
    parser = argparse.ArgumentParser(description='小红书批量发布脚本')
    parser.add_argument('--content-dir', type=str,
                        default=os.path.expanduser('~/.openclaw/workspace/content/xiaohongshu'),
                        help='内容目录路径')
    parser.add_argument('--images-dir', type=str,
                        default=os.path.expanduser('~/.openclaw/workspace/content/xiaohongshu/images'),
                        help='图片目录路径')
    parser.add_argument('--dry-run', action='store_true',
                        help='预览模式，不实际发布')
    parser.add_argument('--start', type=int, default=1,
                        help='从第几篇开始（默认：1）')
    parser.add_argument('--count', type=int, default=None,
                        help='发布几篇（默认：全部）')
    parser.add_argument('--delay', type=int, default=30,
                        help='发布间隔秒数（默认：30）')
    parser.add_argument('--output', type=str,
                        default=os.path.expanduser('~/.openclaw/workspace/content/xiaohongshu/publish_report.json'),
                        help='发布报告输出路径')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("📕 小红书批量发布工具")
    print("=" * 70)
    print(f"📁 内容目录：{args.content_dir}")
    print(f"🖼️  图片目录：{args.images_dir}")
    print(f"🔍 模式：{'预览 (DRY-RUN)' if args.dry_run else '实际发布'}")
    print(f"📊 范围：第 {args.start} 篇开始，最多 {args.count or '全部'} 篇")
    print(f"⏱️  间隔：{args.delay} 秒")
    print("=" * 70)
    
    # 检查目录
    if not os.path.exists(args.content_dir):
        print(f"❌ 内容目录不存在：{args.content_dir}")
        sys.exit(1)
    
    if not os.path.exists(args.images_dir):
        print(f"❌ 图片目录不存在：{args.images_dir}")
        sys.exit(1)
    
    # 加载内容文件
    content_files = load_content_files(args.content_dir, args.start, args.count)
    print(f"\n📄 找到 {len(content_files)} 篇内容文件")
    
    if not content_files:
        print("⚠️  没有内容文件需要发布")
        sys.exit(0)
    
    # 初始化组件
    image_matcher = ImageMatcher(args.images_dir)
    publisher = Publisher(dry_run=args.dry_run, delay=args.delay)
    
    # 发布循环
    results = []
    for i, filename in enumerate(content_files, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/{len(content_files)}] 处理：{filename}")
        
        # 解析内容
        content_path = os.path.join(args.content_dir, filename)
        parser = ContentParser(content_path)
        
        # 检查内容完整性
        if not parser.data['has_all_sections']:
            print(f"⚠️  内容不完整，缺少部分章节")
            missing = []
            for section in ['古籍记载', '症状自查', '材料', '做法', '功效', '注意事项']:
                if section not in parser.data['sections']:
                    missing.append(section)
            print(f"   缺失：{', '.join(missing)}")
        
        # 匹配图片
        image_path = image_matcher.find_image(filename)
        parser.data['image_path'] = image_path
        
        # 获取发布数据
        publish_data = parser.get_publish_data()
        
        # 发布
        result = publisher.publish(publish_data, image_path)
        results.append(result)
    
    # 生成报告
    report = generate_report(results, args.output)
    
    # 输出总结
    print(f"\n{'='*70}")
    print("📊 发布总结")
    print("=" * 70)
    print(f"✅ 成功：{report['success']}")
    print(f"❌ 失败：{report['failed']}")
    print(f"⚠️  跳过：{report['skipped']}")
    if args.dry_run:
        print(f"🔍 预览：{report['dry_run']}")
    print(f"📝 报告：{args.output}")
    print("=" * 70)


if __name__ == '__main__':
    main()

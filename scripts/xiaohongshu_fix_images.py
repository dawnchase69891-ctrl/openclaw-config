#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书图片修复工具

功能：
1. 检测 images 目录下的真实图片文件（无扩展名但实际是 WebP 格式）
2. 删除假的 .webp 文件（Cloudflare 验证页面）
3. 将真实图片复制并重命名为正确的 .webp 格式
4. 验证图片有效性

使用方法：
    python scripts/xiaohongshu_fix_images.py --content-dir ~/.openclaw/workspace/content/xiaohongshu
"""

import os
import sys
import shutil
import argparse
from pathlib import Path


def is_real_webp(file_path: str) -> bool:
    """检查文件是否是真实的 WebP 图片"""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(12)
            # WebP 文件头：RIFF....WEBP
            return header[:4] == b'RIFF' and header[8:12] == b'WEBP'
    except Exception:
        return False


def is_html_file(file_path: str) -> bool:
    """检查文件是否是 HTML（Cloudflare 验证页面）"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(200)
            return '<!DOCTYPE html>' in content or 'Cloudflare' in content
    except Exception:
        return False


def get_content_files(content_dir: str) -> list:
    """获取所有内容文件（.md）"""
    content_files = []
    for f in os.listdir(content_dir):
        if f.endswith('.md') and not f.startswith('_'):
            # 排除辅助文件
            if f not in ['封面图提示词.md', '古籍知识库.md', '配图清单.md', '配图制作资源表.md']:
                content_files.append(f)
    return sorted(content_files)


def find_real_images(images_dir: str) -> dict:
    """查找所有真实图片文件"""
    real_images = {}
    
    for filename in os.listdir(images_dir):
        file_path = os.path.join(images_dir, filename)
        
        if not os.path.isfile(file_path):
            continue
        
        # 跳过已经是正确命名的 .webp 文件
        if filename.endswith('.webp'):
            if is_real_webp(file_path):
                # 提取基础名称（去掉序号）
                base_name = filename.split('_', 1)[0] if '_' in filename else filename.replace('.webp', '')
                real_images[base_name] = {
                    'path': file_path,
                    'filename': filename,
                    'size': os.path.getsize(file_path),
                    'is_valid': True
                }
            continue
        
        # 检查无扩展名文件
        if is_real_webp(file_path):
            # 尝试从文件名推断对应内容
            base_name = filename.split('_')[0] if '_' in filename else filename
            real_images[base_name] = {
                'path': file_path,
                'filename': filename,
                'size': os.path.getsize(file_path),
                'is_valid': True,
                'needs_rename': True
            }
    
    return real_images


def fix_images(content_dir: str, images_dir: str, dry_run: bool = False) -> dict:
    """修复图片文件"""
    result = {
        'found_real_images': [],
        'fixed_images': [],
        'deleted_fake': [],
        'missing_images': [],
        'errors': []
    }
    
    # 获取内容文件列表
    content_files = get_content_files(content_dir)
    print(f"📄 找到 {len(content_files)} 篇内容文件")
    
    # 查找真实图片
    real_images = find_real_images(images_dir)
    print(f"🖼️  找到 {len(real_images)} 个真实图片文件")
    
    # 处理假的 .webp 文件
    for filename in os.listdir(images_dir):
        if not filename.endswith('.webp'):
            continue
        
        file_path = os.path.join(images_dir, filename)
        if not os.path.isfile(file_path):
            continue
        
        if is_html_file(file_path):
            print(f"❌ 发现假图片：{filename} (Cloudflare 验证页面)")
            if not dry_run:
                os.remove(file_path)
                result['deleted_fake'].append(filename)
                print(f"   ✓ 已删除")
            else:
                print(f"   [DRY-RUN] 将删除")
        elif is_real_webp(file_path):
            print(f"✅ 真实图片：{filename}")
            result['found_real_images'].append(filename)
    
    # 重命名真实图片
    for base_name, info in real_images.items():
        if not info.get('needs_rename', False):
            continue
        
        old_path = info['path']
        old_filename = info['filename']
        
        # 生成新文件名（匹配内容文件）
        # 例如：01_herb -> 01_黄芪红枣茶.webp
        # 需要根据内容文件来确定正确名称
        for content_file in content_files:
            content_num = content_file.split('_')[0]
            if base_name == content_num:
                new_filename = content_file.replace('.md', '.webp')
                new_path = os.path.join(images_dir, new_filename)
                
                # 检查目标文件是否已存在
                if os.path.exists(new_path):
                    if is_real_webp(new_path):
                        print(f"⚠️  目标文件已存在且有效：{new_filename}")
                        continue
                    elif is_html_file(new_path):
                        print(f"🔄 替换假图片：{new_filename}")
                        if not dry_run:
                            os.remove(new_path)
                
                print(f"🔧 重命名：{old_filename} -> {new_filename}")
                if not dry_run:
                    shutil.copy2(old_path, new_path)
                    result['fixed_images'].append({
                        'old': old_filename,
                        'new': new_filename,
                        'size': info['size']
                    })
                    print(f"   ✓ 已复制并重命名")
                else:
                    print(f"   [DRY-RUN] 将复制并重命名")
                break
    
    # 检查缺失的图片
    for content_file in content_files:
        expected_image = content_file.replace('.md', '.webp')
        image_path = os.path.join(images_dir, expected_image)
        
        if not os.path.exists(image_path) or not is_real_webp(image_path):
            result['missing_images'].append({
                'content': content_file,
                'expected_image': expected_image
            })
            print(f"⚠️  缺失图片：{expected_image} (对应 {content_file})")
    
    return result


def main():
    parser = argparse.ArgumentParser(description='小红书图片修复工具')
    parser.add_argument('--content-dir', type=str, 
                        default=os.path.expanduser('~/.openclaw/workspace/content/xiaohongshu'),
                        help='内容目录路径')
    parser.add_argument('--images-dir', type=str,
                        default=os.path.expanduser('~/.openclaw/workspace/content/xiaohongshu/images'),
                        help='图片目录路径')
    parser.add_argument('--dry-run', action='store_true',
                        help='预览模式，不实际修改文件')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔧 小红书图片修复工具")
    print("=" * 60)
    print(f"📁 内容目录：{args.content_dir}")
    print(f"🖼️  图片目录：{args.images_dir}")
    print(f"🔍 模式：{'预览 (DRY-RUN)' if args.dry_run else '实际执行'}")
    print("=" * 60)
    print()
    
    if not os.path.exists(args.content_dir):
        print(f"❌ 内容目录不存在：{args.content_dir}")
        sys.exit(1)
    
    if not os.path.exists(args.images_dir):
        print(f"❌ 图片目录不存在：{args.images_dir}")
        sys.exit(1)
    
    result = fix_images(args.content_dir, args.images_dir, args.dry_run)
    
    print()
    print("=" * 60)
    print("📊 修复报告")
    print("=" * 60)
    print(f"✅ 找到的真实图片：{len(result['found_real_images'])}")
    print(f"🔧 已修复的图片：{len(result['fixed_images'])}")
    print(f"❌ 已删除的假图片：{len(result['deleted_fake'])}")
    print(f"⚠️  仍缺失的图片：{len(result['missing_images'])}")
    
    if result['fixed_images']:
        print("\n📝 修复详情:")
        for item in result['fixed_images']:
            print(f"  • {item['old']} -> {item['new']} ({item['size'] / 1024:.1f} KB)")
    
    if result['missing_images']:
        print("\n⚠️  缺失图片列表:")
        for item in result['missing_images']:
            print(f"  • {item['expected_image']} (对应 {item['content']})")
    
    print()
    print("=" * 60)
    print("✨ 图片修复完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()

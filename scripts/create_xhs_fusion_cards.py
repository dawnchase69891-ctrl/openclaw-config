#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书图文融合卡片生成器 v2.0
文字和图片自然融合，无割裂感
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os

# 颜色配置
COLORS = {
    'primary': '#FF6B35',      # 暖橙色
    'secondary': '#7CB342',    # 浅绿色
    'text_dark': '#1F2937',
    'text_light': '#FFFFFF',
    'overlay': '#000000',      # 遮罩颜色
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_fusion_cover(title: str, subtitle: str, image_path: str, output_path: str, width=1080, height=1440):
    """创建图文融合封面 - 图片作为背景，文字叠加"""
    
    # 创建画布
    canvas = Image.new('RGB', (width, height), hex_to_rgb('#FFFFFF'))
    
    # 加载背景图片，铺满整个画布
    if os.path.exists(image_path):
        bg = Image.open(image_path)
        # 裁剪并缩放以填满画布
        bg_ratio = bg.width / bg.height
        canvas_ratio = width / height
        if bg_ratio > canvas_ratio:
            # 图片更宽，按高度裁剪
            new_height = bg.height
            new_width = int(new_height * canvas_ratio)
            left = (bg.width - new_width) // 2
            bg = bg.crop((left, 0, left + new_width, new_height))
        else:
            # 图片更高，按宽度裁剪
            new_width = bg.width
            new_height = int(new_width / canvas_ratio)
            top = (bg.height - new_height) // 2
            bg = bg.crop((0, top, new_width, new_height))
        bg = bg.resize((width, height), Image.LANCZOS)
        
        # 添加渐变遮罩（从透明到半透明黑色）
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        for y in range(height):
            # 从上到下，遮罩透明度递增（0 -> 180）
            alpha = int(180 * (y / height))
            for x in range(width):
                overlay.putpixel((x, y), (0, 0, 0, alpha))
        
        bg = bg.convert('RGBA')
        bg = Image.alpha_composite(bg, overlay)
        canvas = bg.convert('RGB')
    
    draw = ImageDraw.Draw(canvas)
    
    # 加载字体
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 80)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 40)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
    
    # 计算标题位置（底部居中）
    title_y = int(height * 0.65)
    
    # 自动换行
    def wrap_text(text, max_chars):
        lines = []
        line = ""
        for char in text:
            if len(line) >= max_chars:
                lines.append(line)
                line = char
            else:
                line += char
        if line:
            lines.append(line)
        return lines
    
    title_lines = wrap_text(title, 8)
    
    # 绘制标题（白色带阴影）
    for i, line in enumerate(title_lines[:3]):
        text_width = font_title.getsize(line)[0] if hasattr(font_title, 'getsize') else len(line) * 60
        x = (width - text_width) // 2
        y = title_y + i * 100
        # 阴影
        draw.text((x+3, y+3), line, font=font_title, fill=(0, 0, 0, 100))
        # 主文字
        draw.text((x, y), line, font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 副标题
    if subtitle:
        sub_y = title_y + len(title_lines) * 100 + 20
        text_width = font_sub.getsize(subtitle)[0] if hasattr(font_sub, 'getsize') else len(subtitle) * 30
        x = (width - text_width) // 2
        draw.text((x, sub_y), subtitle, font=font_sub, fill=hex_to_rgb(COLORS['text_light']))
    
    # 底部装饰线
    draw.rectangle([60, height-80, width-60, height-78], fill=hex_to_rgb(COLORS['primary']))
    
    canvas.save(output_path, quality=95)
    print(f"✅ 封面已保存: {output_path}")

def create_fusion_card(title: str, content_lines: list, image_path: str, output_path: str, width=1080, height=1440):
    """创建图文融合卡片 - 图片在右侧或底部，文字自然融入"""
    
    # 加载背景图片
    bg_img = None
    if image_path and os.path.exists(image_path):
        bg_img = Image.open(image_path)
        # 调整为合适大小
        bg_img = bg_img.resize((width, int(width * bg_img.height / bg_img.width)), Image.LANCZOS)
        if bg_img.height > height:
            bg_img = bg_img.crop((0, 0, width, height))
    
    # 创建画布
    canvas = Image.new('RGB', (width, height), hex_to_rgb('#F9FAFB'))
    draw = ImageDraw.Draw(canvas)
    
    # 加载字体
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 48)
        font_content = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 34)
    except:
        font_title = ImageFont.load_default()
        font_content = ImageFont.load_default()
    
    # 顶部标题栏
    draw.rectangle([0, 0, width, 100], fill=hex_to_rgb(COLORS['primary']))
    text_width = font_title.getsize(title)[0] if hasattr(font_title, 'getsize') else len(title) * 35
    draw.text(((width - text_width) // 2, 25), title, font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 内容区域
    y = 130
    for item in content_lines:
        if y > height - 450:  # 留出图片空间
            break
        if item.startswith('•'):
            # 列表项
            draw.text((60, y), item, font=font_content, fill=hex_to_rgb(COLORS['text_dark']))
        elif item == '':
            y += 20  # 空行
            continue
        else:
            draw.text((60, y), item, font=font_content, fill=hex_to_rgb(COLORS['text_dark']))
        y += 55
    
    # 底部图片区域（圆角矩形裁剪）
    if bg_img:
        # 计算图片位置
        img_height = min(400, bg_img.height)
        img_y = height - img_height - 40
        
        # 创建圆角遮罩
        mask = Image.new('L', (width - 80, img_height), 255)
        
        # 裁剪图片
        bg_cropped = bg_img.resize((width - 80, img_height), Image.LANCZOS)
        
        # 粘贴到画布
        canvas.paste(bg_cropped, (40, img_y))
        
        # 添加底部渐变遮罩（让图片融入背景）
        for i in range(30):
            alpha = int(255 * (i / 30))
            y_pos = img_y - 30 + i
            for x in range(width):
                pixel = canvas.getpixel((x, y_pos))
                new_color = (
                    int(pixel[0] * alpha / 255 + 249 * (255 - alpha) / 255),
                    int(pixel[1] * alpha / 255 + 250 * (255 - alpha) / 255),
                    int(pixel[2] * alpha / 255 + 251 * (255 - alpha) / 255)
                )
                canvas.putpixel((x, y_pos), new_color)
    
    # 底部装饰
    draw.rectangle([0, height-5, width, height], fill=hex_to_rgb(COLORS['secondary']))
    
    canvas.save(output_path, quality=95)
    print(f"✅ 卡片已保存: {output_path}")

def create_ending_card(title: str, content_lines: list, output_path: str, width=1080, height=1440):
    """创建结尾卡片（无图片，纯文字）"""
    canvas = Image.new('RGB', (width, height), hex_to_rgb('#F9FAFB'))
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 48)
        font_content = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 34)
    except:
        font_title = ImageFont.load_default()
        font_content = ImageFont.load_default()
    
    # 顶部标题栏
    draw.rectangle([0, 0, width, 100], fill=hex_to_rgb(COLORS['primary']))
    text_width = font_title.getsize(title)[0] if hasattr(font_title, 'getsize') else len(title) * 35
    draw.text(((width - text_width) // 2, 25), title, font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 内容居中
    y = 200
    for item in content_lines:
        text_width = font_content.getsize(item)[0] if hasattr(font_content, 'getsize') else len(item) * 25
        x = (width - text_width) // 2
        draw.text((x, y), item, font=font_content, fill=hex_to_rgb(COLORS['text_dark']))
        y += 70
    
    # 底部品牌
    draw.rectangle([0, height-100, width, height], fill=hex_to_rgb(COLORS['secondary']))
    brand = "🌿 赤兔养生计划 · 一起健康养生"
    text_width = font_content.getsize(brand)[0] if hasattr(font_content, 'getsize') else len(brand) * 25
    draw.text(((width - text_width) // 2, height-70), brand, font=font_content, fill=hex_to_rgb(COLORS['text_light']))
    
    canvas.save(output_path, quality=95)
    print(f"✅ 结尾卡片已保存: {output_path}")

def main():
    output_dir = os.path.expanduser("~/.openclaw/media/xhs-fusion/")
    os.makedirs(output_dir, exist_ok=True)
    
    # 素材路径
    goji_img = os.path.expanduser("~/.openclaw/media/素材_枸杞.jpg")
    chrysanthemum_img = os.path.expanduser("~/.openclaw/media/素材_菊花.jpg")
    tea_img = os.path.expanduser("~/.openclaw/media/素材_养生茶.jpg")
    goji_tea_img = os.path.expanduser("~/.openclaw/media/素材_枸杞菊花茶_1.jpg")
    
    print("🎨 开始生成图文融合卡片...\n")
    
    # 1. 封面 - 图片铺满背景，文字叠加
    create_fusion_cover(
        title="熬夜党必喝！",
        subtitle="3种茶护眼明目 · 赤兔养生计划",
        image_path=tea_img,
        output_path=os.path.join(output_dir, "01_封面.png")
    )
    
    # 2. 原料卡片
    create_fusion_card(
        title="🌿 原料准备",
        content_lines=[
            "• 枸杞 10g",
            "  补肾生精，养肝明目",
            "",
            "• 菊花 5朵",
            "  清肝明目，清热解毒",
            "",
            "• 决明子 5g",
            "  清肝明目，润肠通便"
        ],
        image_path=goji_img,
        output_path=os.path.join(output_dir, "02_原料.png")
    )
    
    # 3. 方法卡片
    create_fusion_card(
        title="🍵 冲泡方法",
        content_lines=[
            "Step 1 · 材料洗净",
            "枸杞、菊花冲洗干净",
            "",
            "Step 2 · 放入杯中",
            "所有材料放入茶杯",
            "",
            "Step 3 · 热水冲泡",
            "85℃热水焖泡5-8分钟"
        ],
        image_path=tea_img,
        output_path=os.path.join(output_dir, "03_方法.png")
    )
    
    # 4. 功效卡片
    create_fusion_card(
        title="✨ 护眼功效",
        content_lines=[
            "清肝明目",
            "缓解眼干、眼涩、眼疲劳",
            "",
            "滋补肝肾",
            "改善视力模糊、夜盲症",
            "",
            "抗氧化",
            "延缓眼睛衰老，保护视网膜"
        ],
        image_path=chrysanthemum_img,
        output_path=os.path.join(output_dir, "04_功效.png")
    )
    
    # 5. 结尾卡片
    create_ending_card(
        title="💡 温馨提示",
        content_lines=[
            "最佳饮用时间：下午3-5点",
            "",
            "每天一杯，坚持2周见效",
            "",
            "孕妇慎用决明子",
            "",
            "👆 点赞收藏，不迷路"
        ],
        output_path=os.path.join(output_dir, "05_提示.png")
    )
    
    print(f"\n✅ 所有图文融合卡片生成完成！")
    print(f"📂 保存位置: {output_dir}")

if __name__ == "__main__":
    main()
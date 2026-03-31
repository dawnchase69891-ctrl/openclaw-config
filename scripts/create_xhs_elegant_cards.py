#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书精致配图生成器 v4.0
高级设计感：渐变、装饰元素、精致排版
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math

# 配置
WIDTH = 1242
HEIGHT = 1660

# 高级配色（莫兰迪+温暖养生）
COLORS = {
    'primary': '#D4845F',       # 暖棕橙（莫兰迪调）
    'secondary': '#8BA888',     # 灰绿色
    'accent': '#C4A77D',        # 金褐色
    'text_dark': '#3D3D3D',
    'text_gray': '#6B6B6B',
    'text_light': '#FFFFFF',
    'bg_cream': '#FDF8F3',      # 奶油色背景
    'bg_light': '#FAFAFA',
    'line_light': '#E8E8E8',
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def load_font(size, bold=False):
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def draw_decorative_corner(draw, x, y, size, color):
    """绘制装饰角标"""
    color = hex_to_rgb(color)
    # 左上角装饰
    draw.line([x, y, x + size, y], fill=color, width=2)
    draw.line([x, y, x, y + size], fill=color, width=2)

def draw_wave_decoration(draw, y, width, color, amplitude=10, wavelength=40):
    """绘制波浪装饰线"""
    color = hex_to_rgb(color)
    points = []
    for x in range(0, width + 1, 5):
        y_pos = y + amplitude * math.sin(x / wavelength * 2 * math.pi)
        points.append((x, int(y_pos)))
    if len(points) > 1:
        draw.line(points, fill=color, width=2, smooth=True)

def create_elegant_cover(title: str, subtitle: str, image_path: str, output_path: str):
    """精致封面设计"""
    # 画布
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    
    # 加载背景图片
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img_ratio = img.width / img.height
        canvas_ratio = WIDTH / HEIGHT
        
        # 智能裁剪
        if img_ratio > canvas_ratio:
            new_width = int(img.height * canvas_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        else:
            new_height = int(img.width / canvas_ratio)
            top = int((img.height - new_height) * 0.3)
            img = img.crop((0, top, img.width, top + new_height))
        
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        
        # 轻微模糊处理背景
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # 渐变遮罩
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        for y in range(HEIGHT):
            alpha = int(min(200, y / HEIGHT * 220))
            for x in range(WIDTH):
                overlay.putpixel((x, y), (0, 0, 0, alpha))
        
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        canvas = img.convert('RGB')
    
    draw = ImageDraw.Draw(canvas)
    
    # 字体
    font_title = load_font(96, bold=True)
    font_sub = load_font(42)
    font_small = load_font(32)
    
    # 顶部装饰线
    draw.rectangle([80, 60, 100, 60], fill=hex_to_rgb(COLORS['accent']))
    draw.rectangle([80, 60, WIDTH - 80, 62], fill=hex_to_rgb(COLORS['accent']))
    
    # 标题
    title_y = int(HEIGHT * 0.55)
    
    def wrap_text(text, max_width, font):
        lines = []
        line = ""
        for char in text:
            test_line = line + char
            if font.getsize(test_line)[0] > max_width:
                if line:
                    lines.append(line)
                line = char
            else:
                line = test_line
        if line:
            lines.append(line)
        return lines
    
    title_lines = wrap_text(title, WIDTH - 120, font_title)
    
    # 绘制标题（增加文字阴影和描边效果）
    line_height = 110
    total_height = len(title_lines) * line_height
    start_y = title_y - total_height // 2
    
    for i, line in enumerate(title_lines):
        text_width = font_title.getsize(line)[0]
        x = (WIDTH - text_width) // 2
        y = start_y + i * line_height
        
        # 文字外发光效果
        for offset in range(3, 0, -1):
            alpha = 60 - offset * 15
            draw.text((x + offset, y + offset), line, font=font_title, fill=(0, 0, 0, alpha))
        
        # 主文字
        draw.text((x, y), line, font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 副标题背景条
    if subtitle:
        sub_y = start_y + len(title_lines) * line_height + 40
        text_width = font_sub.getsize(subtitle)[0]
        x = (WIDTH - text_width) // 2
        
        # 半透明背景
        padding_x = 30
        padding_y = 15
        draw.rectangle([
            x - padding_x, sub_y - padding_y,
            x + text_width + padding_x, sub_y + 42 + padding_y
        ], fill=hex_to_rgb(COLORS['primary']))
        
        draw.text((x, sub_y), subtitle, font=font_sub, fill=hex_to_rgb(COLORS['text_light']))
    
    # 底部装饰
    draw.rectangle([80, HEIGHT - 60, WIDTH - 80, HEIGHT - 58], fill=hex_to_rgb(COLORS['accent']))
    
    # 品牌标识
    brand = "赤兔养生计划"
    text_width = font_small.getsize(brand)[0]
    draw.text(((WIDTH - text_width) // 2, HEIGHT - 45), brand, font=font_small, fill=hex_to_rgb(COLORS['text_light']))
    
    # 四角装饰
    draw_decorative_corner(draw, 40, 40, 30, COLORS['accent'])
    draw_decorative_corner(draw, WIDTH - 70, 40, 30, COLORS['accent'])
    
    canvas.save(output_path, quality=98, dpi=(150, 150))
    print(f"✅ 封面: {output_path} ({os.path.getsize(output_path)//1024}KB)")

def create_elegant_content_card(title: str, content: list, image_path: str, output_path: str, card_num: int = 1):
    """精致内容卡片"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    draw = ImageDraw.Draw(canvas)
    
    # 字体
    font_title = load_font(48, bold=True)
    font_content = load_font(36)
    font_small = load_font(30)
    font_num = load_font(24, bold=True)
    
    # 顶部装饰条（渐变效果）
    for i in range(8):
        alpha = 255 - i * 25
        draw.rectangle([0, i * 8, WIDTH, (i + 1) * 8], fill=hex_to_rgb(COLORS['primary']))
    
    # 标题区域背景
    draw.rectangle([0, 0, WIDTH, 130], fill=hex_to_rgb(COLORS['bg_cream']))
    
    # 编号标签
    draw.ellipse([50, 40, 90, 80], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((60, 48), f"{card_num}", font=font_num, fill=hex_to_rgb(COLORS['text_light']))
    
    # 标题
    text_width = font_title.getsize(title)[0]
    draw.text((110, 45), title, font=font_title, fill=hex_to_rgb(COLORS['text_dark']))
    
    # 分隔线
    draw.rectangle([50, 145, WIDTH - 50, 147], fill=hex_to_rgb(COLORS['line_light']))
    
    # 内容区域
    y = 180
    left_margin = 70
    line_height = 55
    
    for item in content:
        if y > HEIGHT - 450:
            break
        
        if item == '':
            y += 25
            continue
        elif item.startswith('•'):
            # 列表项带装饰点
            draw.ellipse([left_margin, y + 12, left_margin + 10, y + 22], fill=hex_to_rgb(COLORS['primary']))
            draw.text((left_margin + 25, y), item[1:].strip(), font=font_content, fill=hex_to_rgb(COLORS['text_dark']))
        elif item.startswith('  '):
            # 缩进内容（灰色小字）
            draw.text((left_margin + 25, y), item.strip(), font=font_small, fill=hex_to_rgb(COLORS['text_gray']))
        elif item.startswith('Step'):
            # 步骤标题
            draw.text((left_margin, y), item, font=font_content, fill=hex_to_rgb(COLORS['primary']))
        else:
            draw.text((left_margin, y), item, font=font_content, fill=hex_to_rgb(COLORS['text_dark']))
        y += line_height
    
    # 图片区域
    if image_path and os.path.exists(image_path):
        img = Image.open(image_path)
        
        max_img_width = WIDTH - 100
        max_img_height = 380
        
        img_ratio = img.width / img.height
        if img_ratio > max_img_width / max_img_height:
            img_width = max_img_width
            img_height = int(img_width / img_ratio)
        else:
            img_height = max_img_height
            img_width = int(img_height * img_ratio)
        
        img = img.resize((img_width, img_height), Image.LANCZOS)
        
        # 图片边框装饰
        x = (WIDTH - img_width) // 2
        y = HEIGHT - img_height - 100
        
        # 边框
        border_color = hex_to_rgb(COLORS['accent'])
        border_width = 3
        draw.rectangle([x - border_width, y - border_width, x + img_width + border_width, y + img_height + border_width], outline=border_color, width=border_width)
        
        canvas.paste(img, (x, y))
    
    # 底部装饰线
    draw.rectangle([0, HEIGHT - 10, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    
    canvas.save(output_path, quality=98, dpi=(150, 150))
    print(f"✅ 卡片{card_num}: {output_path} ({os.path.getsize(output_path)//1024}KB)")

def create_elegant_ending_card(title: str, content: list, output_path: str):
    """精致结尾卡片"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(48, bold=True)
    font_content = load_font(36)
    font_brand = load_font(38, bold=True)
    font_tag = load_font(28)
    
    # 顶部装饰条
    for i in range(8):
        draw.rectangle([0, i * 8, WIDTH, (i + 1) * 8], fill=hex_to_rgb(COLORS['primary']))
    
    # 标题
    draw.rectangle([0, 0, WIDTH, 130], fill=hex_to_rgb(COLORS['bg_cream']))
    text_width = font_title.getsize(title)[0]
    draw.text(((WIDTH - text_width) // 2, 45), title, font=font_title, fill=hex_to_rgb(COLORS['text_dark']))
    
    # 分隔线
    draw.rectangle([50, 145, WIDTH - 50, 147], fill=hex_to_rgb(COLORS['line_light']))
    
    # 内容居中
    y = 350
    line_height = 70
    for item in content:
        if item == '':
            y += 35
            continue
        text_width = font_content.getsize(item)[0]
        x = (WIDTH - text_width) // 2
        draw.text((x, y), item, font=font_content, fill=hex_to_rgb(COLORS['text_dark']))
        y += line_height
    
    # 底部品牌区
    brand_height = 180
    draw.rectangle([0, HEIGHT - brand_height, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    
    # 品牌logo装饰
    draw.ellipse([(WIDTH - 60) // 2, HEIGHT - brand_height + 20, (WIDTH + 60) // 2, HEIGHT - brand_height + 80], fill=hex_to_rgb(COLORS['text_light']))
    draw.text(((WIDTH - 40) // 2, HEIGHT - brand_height + 35), "🌿", font=font_brand, fill=hex_to_rgb(COLORS['secondary']))
    
    # 品牌名
    brand_text = "赤兔养生计划"
    text_width = font_brand.getsize(brand_text)[0]
    draw.text(((WIDTH - text_width) // 2, HEIGHT - 90), brand_text, font=font_brand, fill=hex_to_rgb(COLORS['text_light']))
    
    # 标签
    tags = "#赤兔养生计划 #职场养生 #中医养生"
    text_width = font_tag.getsize(tags)[0]
    draw.text(((WIDTH - text_width) // 2, HEIGHT - 45), tags, font=font_tag, fill=hex_to_rgb(COLORS['text_light']))
    
    canvas.save(output_path, quality=98, dpi=(150, 150))
    print(f"✅ 结尾: {output_path} ({os.path.getsize(output_path)//1024}KB)")

def main():
    output_dir = os.path.expanduser("~/.openclaw/media/xhs-elegant/")
    os.makedirs(output_dir, exist_ok=True)
    
    # 素材
    goji_img = os.path.expanduser("~/.openclaw/media/素材_枸杞.jpg")
    chrysanthemum_img = os.path.expanduser("~/.openclaw/media/素材_菊花.jpg")
    tea_img = os.path.expanduser("~/.openclaw/media/素材_养生茶.jpg")
    
    print("🎨 开始生成精致配图...\n")
    
    # 1. 封面
    create_elegant_cover(
        title="熬夜党必喝！",
        subtitle="3种茶护眼明目",
        image_path=tea_img,
        output_path=os.path.join(output_dir, "01_封面.png")
    )
    
    # 2. 原料
    create_elegant_content_card(
        title="🌿 原料准备",
        content=[
            "枸杞 10g",
            "  补肾生精，养肝明目",
            "",
            "菊花 5朵",
            "  清肝明目，清热解毒",
            "",
            "决明子 5g",
            "  清肝明目，润肠通便"
        ],
        image_path=goji_img,
        output_path=os.path.join(output_dir, "02_原料.png"),
        card_num=1
    )
    
    # 3. 方法
    create_elegant_content_card(
        title="🍵 冲泡方法",
        content=[
            "Step 1 · 材料洗净",
            "  枸杞、菊花冲洗干净",
            "",
            "Step 2 · 放入杯中",
            "  所有材料放入茶杯",
            "",
            "Step 3 · 热水冲泡",
            "  85℃热水焖泡5-8分钟"
        ],
        image_path=tea_img,
        output_path=os.path.join(output_dir, "03_方法.png"),
        card_num=2
    )
    
    # 4. 功效
    create_elegant_content_card(
        title="✨ 护眼功效",
        content=[
            "清肝明目",
            "  缓解眼干、眼涩、眼疲劳",
            "",
            "滋补肝肾",
            "  改善视力模糊、夜盲症",
            "",
            "抗氧化",
            "  延缓眼睛衰老，保护视网膜"
        ],
        image_path=chrysanthemum_img,
        output_path=os.path.join(output_dir, "04_功效.png"),
        card_num=3
    )
    
    # 5. 结尾
    create_elegant_ending_card(
        title="💡 温馨提示",
        content=[
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
    
    print(f"\n✅ 所有精致配图生成完成！")
    print(f"📂 位置: {output_dir}")

if __name__ == "__main__":
    main()
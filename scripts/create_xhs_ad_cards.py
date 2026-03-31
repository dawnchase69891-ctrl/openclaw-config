#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书广告级配图设计器 v5.0
专业广告设计师视角：图文混排、视觉冲击、信息饱满
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import math

# 配置
WIDTH = 1242
HEIGHT = 1660

# 专业广告配色
COLORS = {
    'primary': '#E85D04',       # 活力橙
    'secondary': '#2D6A4F',     # 深森绿
    'accent': '#F4A261',        # 暖金橙
    'text_dark': '#1A1A1A',
    'text_gray': '#4A4A4A',
    'text_light': '#FFFFFF',
    'bg_white': '#FFFFFF',
    'bg_cream': '#FFFBF5',
    'shadow': '#00000020',
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

def create_magazine_cover(title: str, subtitle: str, image_path: str, output_path: str):
    """
    杂志风封面 - 大图+大字
    """
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    
    # 背景图（占70%高度）
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img_ratio = img.width / img.height
        target_height = int(HEIGHT * 0.7)
        target_width = int(target_height * img_ratio)
        
        if target_width < WIDTH:
            target_width = WIDTH
            target_height = int(target_width / img_ratio)
        
        # 居中裁剪
        if target_width > WIDTH:
            left = (target_width - WIDTH) // 2
            img = img.resize((target_width, target_height), Image.LANCZOS)
            img = img.crop((left, 0, left + WIDTH, target_height))
        else:
            top = (target_height - int(HEIGHT * 0.7)) // 2
            img = img.resize((target_width, target_height), Image.LANCZOS)
            img = img.crop((0, top, target_width, top + int(HEIGHT * 0.7)))
        
        canvas.paste(img, (0, 0))
    
    draw = ImageDraw.Draw(canvas)
    
    # 底部渐变遮罩（让文字清晰）
    for y in range(int(HEIGHT * 0.5), HEIGHT):
        alpha = int(255 * (y - HEIGHT * 0.5) / (HEIGHT * 0.5))
        for x in range(WIDTH):
            pixel = canvas.getpixel((x, y))
            # 渐变到白色
            new_r = int(pixel[0] * (255 - alpha) / 255 + 255 * alpha / 255)
            new_g = int(pixel[1] * (255 - alpha) / 255 + 255 * alpha / 255)
            new_b = int(pixel[2] * (255 - alpha) / 255 + 255 * alpha / 255)
            canvas.putpixel((x, y), (new_r, new_g, new_b))
    
    draw = ImageDraw.Draw(canvas)
    
    # 字体
    font_title = load_font(100, bold=True)
    font_sub = load_font(48)
    font_brand = load_font(36)
    
    # 大标题（底部）
    title_y = int(HEIGHT * 0.72)
    
    # 自动换行
    def wrap_text(text, max_width, font):
        lines = []
        line = ""
        for char in text:
            if font.getsize(line + char)[0] > max_width:
                if line:
                    lines.append(line)
                line = char
            else:
                line += char
        if line:
            lines.append(line)
        return lines
    
    title_lines = wrap_text(title, WIDTH - 100, font_title)
    
    # 绘制标题
    for i, line in enumerate(title_lines):
        text_width = font_title.getsize(line)[0]
        x = 50
        y = title_y + i * 110
        draw.text((x, y), line, font=font_title, fill=hex_to_rgb(COLORS['primary']))
    
    # 副标题
    sub_y = title_y + len(title_lines) * 110 + 20
    draw.text((50, sub_y), subtitle, font=font_sub, fill=hex_to_rgb(COLORS['text_gray']))
    
    # 底部品牌栏
    draw.rectangle([0, HEIGHT - 80, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, HEIGHT - 60), "🌿 赤兔养生计划", font=font_brand, fill=hex_to_rgb(COLORS['text_light']))
    
    canvas.save(output_path, quality=98, dpi=(150, 150))
    print(f"✅ 封面: {output_path}")

def create_magazine_card(title: str, main_content: str, detail_items: list, image_path: str, output_path: str, card_num: int = 1):
    """
    杂志风内容卡片 - 图文混排，左图右文
    """
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    draw = ImageDraw.Draw(canvas)
    
    # 字体
    font_title = load_font(52, bold=True)
    font_main = load_font(44, bold=True)
    font_detail = load_font(34)
    font_num = load_font(28, bold=True)
    
    # 顶部编号+标题
    draw.rectangle([0, 0, WIDTH, 100], fill=hex_to_rgb(COLORS['secondary']))
    draw.ellipse([40, 30, 70, 60], fill=hex_to_rgb(COLORS['accent']))
    draw.text((48, 32), str(card_num), font=font_num, fill=hex_to_rgb(COLORS['text_dark']))
    draw.text((90, 30), title, font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 左侧图片（占60%宽度）
    img_width = int(WIDTH * 0.55)
    img_height = int(HEIGHT * 0.55)
    
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img_ratio = img.width / img.height
        target_ratio = img_width / img_height
        
        if img_ratio > target_ratio:
            new_height = img_height
            new_width = int(new_height * img_ratio)
            left = (new_width - img_width) // 2
            img = img.resize((new_width, new_height), Image.LANCZOS)
            img = img.crop((left, 0, left + img_width, new_height))
        else:
            new_width = img_width
            new_height = int(new_width / img_ratio)
            top = (new_height - img_height) // 2
            img = img.resize((new_width, new_height), Image.LANCZOS)
            img = img.crop((0, top, new_width, top + img_height))
        
        canvas.paste(img, (40, 140))
        
        # 图片边框
        draw.rectangle([40, 140, 40 + img_width, 140 + img_height], outline=hex_to_rgb(COLORS['accent']), width=3)
    
    # 右侧文字区域
    text_x = img_width + 70
    text_y = 160
    text_width = WIDTH - text_x - 40
    
    # 主要内容（大字）
    if main_content:
        draw.text((text_x, text_y), main_content, font=font_main, fill=hex_to_rgb(COLORS['primary']))
        text_y += 70
    
    # 详细条目
    for item in detail_items:
        if text_y > HEIGHT - 200:
            break
        
        if item == '':
            text_y += 20
            continue
        
        # 自动换行
        words = item
        if font_detail.getsize(words)[0] > text_width:
            # 需要换行
            line = ""
            for char in words:
                if font_detail.getsize(line + char)[0] > text_width:
                    draw.text((text_x, text_y), line, font=font_detail, fill=hex_to_rgb(COLORS['text_gray']))
                    text_y += 45
                    line = char
                else:
                    line += char
            if line:
                draw.text((text_x, text_y), line, font=font_detail, fill=hex_to_rgb(COLORS['text_gray']))
                text_y += 45
        else:
            draw.text((text_x, text_y), item, font=font_detail, fill=hex_to_rgb(COLORS['text_gray']))
            text_y += 50
    
    # 底部装饰
    draw.rectangle([0, HEIGHT - 15, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['primary']))
    
    canvas.save(output_path, quality=98, dpi=(150, 150))
    print(f"✅ 卡片{card_num}: {output_path}")

def create_full_image_card(title: str, content_lines: list, image_path: str, output_path: str, card_num: int = 1):
    """
    全图卡片 - 图片占满，文字浮动在图片上
    """
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    
    # 图片占满整个卡片
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img_ratio = img.width / img.height
        canvas_ratio = WIDTH / HEIGHT
        
        if img_ratio > canvas_ratio:
            new_height = HEIGHT
            new_width = int(new_height * img_ratio)
            left = (new_width - WIDTH) // 2
            img = img.resize((new_width, new_height), Image.LANCZOS)
            img = img.crop((left, 0, left + WIDTH, new_height))
        else:
            new_width = WIDTH
            new_height = int(new_width / img_ratio)
            top = int((new_height - HEIGHT) * 0.3)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            img = img.crop((0, top, new_width, top + HEIGHT))
        
        canvas.paste(img, (0, 0))
    
    draw = ImageDraw.Draw(canvas)
    
    # 底部渐变遮罩（深色）
    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    for y in range(int(HEIGHT * 0.4), HEIGHT):
        alpha = int(200 * (y - HEIGHT * 0.4) / (HEIGHT * 0.6))
        for x in range(WIDTH):
            overlay.putpixel((x, y), (0, 0, 0, alpha))
    
    canvas_rgba = canvas.convert('RGBA')
    canvas_rgba = Image.alpha_composite(canvas_rgba, overlay)
    canvas = canvas_rgba.convert('RGB')
    draw = ImageDraw.Draw(canvas)
    
    # 字体
    font_title = load_font(56, bold=True)
    font_content = load_font(40)
    
    # 标题（底部）
    y = int(HEIGHT * 0.55)
    draw.text((50, y), title, font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    y += 80
    
    # 内容
    for line in content_lines:
        if y > HEIGHT - 150:
            break
        if line == '':
            y += 30
            continue
        draw.text((50, y), line, font=font_content, fill=hex_to_rgb(COLORS['text_light']))
        y += 55
    
    # 卡片编号
    draw.ellipse([WIDTH - 100, HEIGHT - 100, WIDTH - 40, HEIGHT - 40], fill=hex_to_rgb(COLORS['accent']))
    draw.text((WIDTH - 80, HEIGHT - 85), str(card_num), font=load_font(36, bold=True), fill=hex_to_rgb(COLORS['text_dark']))
    
    canvas.save(output_path, quality=98, dpi=(150, 150))
    print(f"✅ 卡片{card_num}: {output_path}")

def create_summary_card(title: str, content_blocks: list, output_path: str):
    """
    总结卡片 - 多栏目布局，信息密集
    """
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(48, bold=True)
    font_block_title = load_font(38, bold=True)
    font_content = load_font(32)
    font_brand = load_font(40, bold=True)
    
    # 顶部标题栏
    draw.rectangle([0, 0, WIDTH, 120], fill=hex_to_rgb(COLORS['primary']))
    draw.text((50, 40), title, font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 内容区块
    y = 150
    for block in content_blocks:
        if y > HEIGHT - 200:
            break
        
        block_title = block.get('title', '')
        items = block.get('items', [])
        
        if block_title:
            draw.rectangle([40, y, 50, y + 30], fill=hex_to_rgb(COLORS['secondary']))
            draw.text((60, y), block_title, font=font_block_title, fill=hex_to_rgb(COLORS['text_dark']))
            y += 50
        
        for item in items:
            if y > HEIGHT - 200:
                break
            draw.text((60, y), f"• {item}", font=font_content, fill=hex_to_rgb(COLORS['text_gray']))
            y += 45
        
        y += 30
    
    # 底部品牌
    draw.rectangle([0, HEIGHT - 150, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, HEIGHT - 120), "🌿 赤兔养生计划", font=font_brand, fill=hex_to_rgb(COLORS['text_light']))
    draw.text((50, HEIGHT - 70), "跟着赤兔，一起健康养生", font=font_content, fill=hex_to_rgb(COLORS['text_light']))
    
    canvas.save(output_path, quality=98, dpi=(150, 150))
    print(f"✅ 总结卡片: {output_path}")

def main():
    output_dir = os.path.expanduser("~/.openclaw/media/xhs-ad/")
    os.makedirs(output_dir, exist_ok=True)
    
    goji_img = os.path.expanduser("~/.openclaw/media/素材_枸杞.jpg")
    chrysanthemum_img = os.path.expanduser("~/.openclaw/media/素材_菊花.jpg")
    tea_img = os.path.expanduser("~/.openclaw/media/素材_养生茶.jpg")
    
    print("🎨 开始生成广告级配图...\n")
    
    # 1. 封面 - 大图+大字
    create_magazine_cover(
        title="熬夜党必喝！",
        subtitle="3种茶护眼明目 · 职场人养生必备",
        image_path=tea_img,
        output_path=os.path.join(output_dir, "01_封面.png")
    )
    
    # 2. 原料卡片 - 全图模式
    create_full_image_card(
        title="🌿 原料准备",
        content_lines=[
            "枸杞 10g | 补肾生精",
            "菊花 5朵 | 清肝明目", 
            "决明子 5g | 润肠通便",
            "",
            "以上材料在药店或网上都能买到"
        ],
        image_path=goji_img,
        output_path=os.path.join(output_dir, "02_原料.png"),
        card_num=1
    )
    
    # 3. 方法卡片 - 图文混排
    create_magazine_card(
        title="冲泡方法",
        main_content="简单三步",
        detail_items=[
            "Step 1：枸杞、菊花、决明子冲洗干净",
            "Step 2：放入养生壶或茶杯",
            "Step 3：85℃热水焖泡5-8分钟",
            "",
            "💡 小贴士：",
            "可反复冲泡2-3次",
            "最佳饮用时间：下午3-5点"
        ],
        image_path=tea_img,
        output_path=os.path.join(output_dir, "03_方法.png"),
        card_num=2
    )
    
    # 4. 功效卡片 - 全图模式
    create_full_image_card(
        title="✨ 护眼功效",
        content_lines=[
            "清肝明目 · 缓解眼干眼涩",
            "滋补肝肾 · 改善视力模糊",
            "抗氧化 · 保护视网膜",
            "",
            "坚持喝2周，眼睛更舒服！"
        ],
        image_path=chrysanthemum_img,
        output_path=os.path.join(output_dir, "04_功效.png"),
        card_num=3
    )
    
    # 5. 总结卡片 - 多栏目
    create_summary_card(
        title="💡 温馨提示",
        content_blocks=[
            {
                'title': '饮用建议',
                'items': [
                    '最佳时间：下午3-5点',
                    '每天一杯，坚持2周见效',
                    '可搭配热敷眼睛效果更佳'
                ]
            },
            {
                'title': '禁忌人群',
                'items': [
                    '孕妇慎用决明子',
                    '脾胃虚寒者不宜空腹饮用',
                    '感冒发烧时暂停饮用'
                ]
            },
            {
                'title': '互动',
                'items': [
                    '👆 点赞收藏，不迷路',
                    '💬 评论区告诉我你的养生心得'
                ]
            }
        ],
        output_path=os.path.join(output_dir, "05_提示.png")
    )
    
    print(f"\n✅ 广告级配图生成完成！")
    print(f"📂 位置: {output_dir}")

if __name__ == "__main__":
    main()
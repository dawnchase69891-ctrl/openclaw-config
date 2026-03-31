#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书高质量配图生成器 v3.0
遵循专业设计原则：不拉伸、保持比例、高清输出
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os

# 配置
WIDTH = 1242  # 小红书推荐宽度
HEIGHT = 1660  # 3:4比例

# 配色方案（温暖养生风格）
COLORS = {
    'primary': '#FF8C42',      # 暖橙色
    'secondary': '#6B8E23',    # 橄榄绿
    'accent': '#8B4513',       # 深褐色
    'text_dark': '#2D3748',
    'text_light': '#FFFFFF',
    'bg_warm': '#FFF8F0',      # 温暖背景
    'bg_card': '#FFFFFF',
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def load_font(size, bold=False):
    """加载字体，优先思源黑体"""
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def create_professional_cover(title: str, subtitle: str, image_path: str, output_path: str):
    """
    专业封面设计
    - 图片铺满背景（裁剪不拉伸）
    - 渐变遮罩保证文字可读
    - 大字标题居中偏下
    """
    # 创建画布
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_warm']))
    
    # 加载背景图片（智能裁剪）
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img_ratio = img.width / img.height
        canvas_ratio = WIDTH / HEIGHT
        
        # 智能裁剪，保持比例
        if img_ratio > canvas_ratio:
            # 图片更宽，按高度裁剪两边
            new_width = int(img.height * canvas_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        else:
            # 图片更高，按宽度裁剪上下
            new_height = int(img.width / canvas_ratio)
            top = (img.height - new_height) // 3  # 偏上裁剪，保留主体
            img = img.crop((0, top, img.width, top + new_height))
        
        # 高质量缩放
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        
        # 添加渐变遮罩（从透明到深色）
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        for y in range(HEIGHT):
            # 从上到下：透明 -> 半透明
            alpha = int(min(180, y / HEIGHT * 200))
            for x in range(WIDTH):
                overlay.putpixel((x, y), (0, 0, 0, alpha))
        
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        canvas = img.convert('RGB')
    
    draw = ImageDraw.Draw(canvas)
    
    # 加载字体
    font_title = load_font(88, bold=True)
    font_sub = load_font(44)
    
    # 标题位置（居中偏下）
    title_y = int(HEIGHT * 0.6)
    
    # 自动换行（每行最多8个字）
    def wrap_text(text, max_width):
        lines = []
        line = ""
        for char in text:
            test_line = line + char
            if font_title.getsize(test_line)[0] > max_width:
                if line:
                    lines.append(line)
                line = char
            else:
                line = test_line
        if line:
            lines.append(line)
        return lines
    
    title_lines = wrap_text(title, WIDTH - 100)
    
    # 绘制标题（白色带阴影）
    line_height = 100
    total_height = len(title_lines) * line_height
    start_y = title_y - total_height // 2
    
    for i, line in enumerate(title_lines):
        text_width = font_title.getsize(line)[0]
        x = (WIDTH - text_width) // 2
        y = start_y + i * line_height
        
        # 阴影效果
        shadow_offset = 4
        draw.text((x + shadow_offset, y + shadow_offset), line, font=font_title, fill=(0, 0, 0, 120))
        # 主文字
        draw.text((x, y), line, font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 副标题
    if subtitle:
        sub_y = start_y + len(title_lines) * line_height + 30
        text_width = font_sub.getsize(subtitle)[0]
        x = (WIDTH - text_width) // 2
        
        # 半透明背景条
        padding = 20
        draw.rectangle([
            x - padding, sub_y - 10,
            x + text_width + padding, sub_y + 50
        ], fill=hex_to_rgb(COLORS['primary']))
        draw.text((x, sub_y), subtitle, font=font_sub, fill=hex_to_rgb(COLORS['text_light']))
    
    # 保存（高质量）
    canvas.save(output_path, quality=98, dpi=(150, 150))
    print(f"✅ 封面已保存: {output_path} ({os.path.getsize(output_path)//1024}KB)")

def create_professional_content_card(title: str, content: list, image_path: str, output_path: str, layout='bottom'):
    """
    专业内容卡片
    - 顶部彩色标题栏
    - 中间文字内容
    - 底部/侧边图片（保持比例）
    """
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_warm']))
    draw = ImageDraw.Draw(canvas)
    
    # 加载字体
    font_title = load_font(52, bold=True)
    font_content = load_font(38)
    font_small = load_font(32)
    
    # 顶部标题栏
    header_height = 120
    draw.rectangle([0, 0, WIDTH, header_height], fill=hex_to_rgb(COLORS['primary']))
    
    # 标题居中
    text_width = font_title.getsize(title)[0]
    draw.text(((WIDTH - text_width) // 2, 35), title, font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 内容区域
    y = header_height + 60
    left_margin = 60
    line_height = 60
    
    for item in content:
        if y > HEIGHT - 500:  # 保留图片空间
            break
        
        if item == '':
            y += 30
            continue
        elif item.startswith('•') or item.startswith('Step'):
            # 列表项/步骤
            draw.text((left_margin, y), item, font=font_content, fill=hex_to_rgb(COLORS['text_dark']))
        elif item.startswith('  '):
            # 缩进内容
            draw.text((left_margin + 40, y), item.strip(), font=font_small, fill=hex_to_rgb(COLORS['accent']))
        else:
            draw.text((left_margin, y), item, font=font_content, fill=hex_to_rgb(COLORS['text_dark']))
        y += line_height
    
    # 图片区域
    if image_path and os.path.exists(image_path):
        img = Image.open(image_path)
        
        # 计算图片尺寸（保持比例）
        max_img_width = WIDTH - 80
        max_img_height = 400
        
        img_ratio = img.width / img.height
        if img_ratio > max_img_width / max_img_height:
            # 图片较宽
            img_width = max_img_width
            img_height = int(img_width / img_ratio)
        else:
            # 图片较高
            img_height = max_img_height
            img_width = int(img_height * img_ratio)
        
        # 高质量缩放
        img = img.resize((img_width, img_height), Image.LANCZOS)
        
        # 居中放置
        x = (WIDTH - img_width) // 2
        y = HEIGHT - img_height - 80
        
        # 添加阴影效果（简化版，不用圆角）
        shadow = Image.new('RGBA', (img_width + 20, img_height + 20), (0, 0, 0, 30))
        
        # 粘贴阴影和图片
        canvas_rgba = canvas.convert('RGBA')
        canvas_rgba.paste(shadow, (x - 5, y - 5))
        
        # 粘贴图片
        canvas_rgba.paste(img, (x, y))
        canvas = canvas_rgba.convert('RGB')
    
    # 底部装饰线
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, HEIGHT - 8, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    
    # 保存
    canvas.save(output_path, quality=98, dpi=(150, 150))
    print(f"✅ 卡片已保存: {output_path} ({os.path.getsize(output_path)//1024}KB)")

def create_ending_card(title: str, content: list, output_path: str):
    """结尾卡片"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_warm']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(52, bold=True)
    font_content = load_font(38)
    
    # 顶部标题栏
    draw.rectangle([0, 0, WIDTH, 120], fill=hex_to_rgb(COLORS['primary']))
    text_width = font_title.getsize(title)[0]
    draw.text(((WIDTH - text_width) // 2, 35), title, font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 内容居中
    y = 300
    line_height = 80
    for item in content:
        if item == '':
            y += 40
            continue
        text_width = font_content.getsize(item)[0]
        x = (WIDTH - text_width) // 2
        draw.text((x, y), item, font=font_content, fill=hex_to_rgb(COLORS['text_dark']))
        y += line_height
    
    # 底部品牌栏
    brand_height = 120
    draw.rectangle([0, HEIGHT - brand_height, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    
    brand_text = "🌿 赤兔养生计划"
    brand_text2 = "跟着赤兔，一起健康养生"
    
    font_brand = load_font(40, bold=True)
    font_brand2 = load_font(32)
    
    text_width = font_brand.getsize(brand_text)[0]
    draw.text(((WIDTH - text_width) // 2, HEIGHT - brand_height + 20), brand_text, font=font_brand, fill=hex_to_rgb(COLORS['text_light']))
    
    text_width = font_brand2.getsize(brand_text2)[0]
    draw.text(((WIDTH - text_width) // 2, HEIGHT - 50), brand_text2, font=font_brand2, fill=hex_to_rgb(COLORS['text_light']))
    
    canvas.save(output_path, quality=98, dpi=(150, 150))
    print(f"✅ 结尾卡片已保存: {output_path} ({os.path.getsize(output_path)//1024}KB)")

def main():
    output_dir = os.path.expanduser("~/.openclaw/media/xhs-pro/")
    os.makedirs(output_dir, exist_ok=True)
    
    # 素材路径
    goji_img = os.path.expanduser("~/.openclaw/media/素材_枸杞.jpg")
    chrysanthemum_img = os.path.expanduser("~/.openclaw/media/素材_菊花.jpg")
    tea_img = os.path.expanduser("~/.openclaw/media/素材_养生茶.jpg")
    
    print("🎨 开始生成高质量配图...\n")
    
    # 1. 封面
    create_professional_cover(
        title="熬夜党必喝！",
        subtitle="3种茶护眼明目",
        image_path=tea_img,
        output_path=os.path.join(output_dir, "01_封面.png")
    )
    
    # 2. 原料卡片
    create_professional_content_card(
        title="🌿 原料准备",
        content=[
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
    create_professional_content_card(
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
        output_path=os.path.join(output_dir, "03_方法.png")
    )
    
    # 4. 功效卡片
    create_professional_content_card(
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
        output_path=os.path.join(output_dir, "04_功效.png")
    )
    
    # 5. 结尾卡片
    create_ending_card(
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
    
    print(f"\n✅ 所有高质量配图生成完成！")
    print(f"📂 保存位置: {output_dir}")
    
    # 显示文件大小
    total_size = sum(os.path.getsize(os.path.join(output_dir, f)) for f in os.listdir(output_dir))
    print(f"📊 总大小: {total_size // 1024}KB")

if __name__ == "__main__":
    main()
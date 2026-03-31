#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书带素材图片卡片生成器
将真实素材图与文字结合，生成更有吸引力的配图卡片
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import sys

# 颜色配置
COLORS = {
    'primary': '#FF6B35',      # 暖橙色
    'secondary': '#7CB342',    # 浅绿色
    'text_dark': '#1F2937',    # 深色文字
    'text_light': '#FFFFFF',   # 浅色文字
    'bg_light': '#F9FAFB',     # 浅色背景
}

def hex_to_rgb(hex_color):
    """十六进制颜色转RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_cover_with_image(title: str, subtitle: str, image_path: str, output_path: str, width=1080, height=1440):
    """创建带素材图片的封面"""
    # 创建画布
    canvas = Image.new('RGB', (width, height), hex_to_rgb('#FFFFFF'))
    draw = ImageDraw.Draw(canvas)
    
    # 加载并处理背景图片
    try:
        bg_image = Image.open(image_path)
        # 调整图片大小以适应画布上半部分
        bg_height = int(height * 0.65)
        bg_image = bg_image.resize((width, bg_height), Image.LANCZOS)
        
        # 添加渐变遮罩
        mask = Image.new('L', (width, bg_height), 0)
        for y in range(bg_height):
            alpha = int(255 * (1 - y / bg_height * 0.3))  # 上亮下暗
            for x in range(width):
                mask.putpixel((x, y), alpha)
        bg_image.putalpha(mask)
        
        # 粘贴到画布
        canvas.paste(bg_image, (0, 0))
    except Exception as e:
        print(f"加载背景图片失败: {e}")
        # 使用纯色背景
        draw.rectangle([0, 0, width, int(height * 0.65)], fill=hex_to_rgb(COLORS['primary']))
    
    # 底部区域（文字区域）
    bottom_height = int(height * 0.35)
    draw.rectangle([0, int(height * 0.65), width, height], fill=hex_to_rgb(COLORS['bg_light']))
    
    # 加载字体
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 72)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 36)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    # 绘制标题
    title_y = int(height * 0.72)
    # 自动换行
    title_lines = []
    line = ""
    for char in title:
        if len(line) >= 10:
            title_lines.append(line)
            line = char
        else:
            line += char
    if line:
        title_lines.append(line)
    
    for i, line in enumerate(title_lines[:3]):  # 最多3行
        text_width = font_large.getsize(line)[0] if hasattr(font_large, 'getsize') else len(line) * 50
        x = (width - text_width) // 2
        draw.text((x, title_y + i * 90), line, font=font_large, fill=hex_to_rgb(COLORS['text_dark']))
    
    # 绘制副标题
    if subtitle:
        subtitle_y = title_y + len(title_lines) * 90 + 30
        text_width = font_medium.getsize(subtitle)[0] if hasattr(font_medium, 'getsize') else len(subtitle) * 25
        x = (width - text_width) // 2
        draw.text((x, subtitle_y), subtitle, font=font_medium, fill=hex_to_rgb(COLORS['secondary']))
    
    # 保存
    canvas.save(output_path, quality=95)
    print(f"✅ 封面已保存: {output_path}")

def create_content_card_with_image(title: str, content: list, image_path: str, output_path: str, width=1080, height=1440):
    """创建带素材图片的内容卡片"""
    # 创建画布
    canvas = Image.new('RGB', (width, height), hex_to_rgb(COLORS['bg_light']))
    draw = ImageDraw.Draw(canvas)
    
    # 加载字体
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 48)
        font_content = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 32)
    except:
        font_title = ImageFont.load_default()
        font_content = ImageFont.load_default()
    
    # 顶部标题区域
    draw.rectangle([0, 0, width, 120], fill=hex_to_rgb(COLORS['primary']))
    text_width = font_title.getsize(title)[0] if hasattr(font_title, 'getsize') else len(title) * 35
    draw.text(((width - text_width) // 2, 35), title, font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 内容区域
    y = 160
    for line in content:
        if y > height - 200:
            break
        draw.text((60, y), line, font=font_content, fill=hex_to_rgb(COLORS['text_dark']))
        y += 60
    
    # 底部素材图片区域
    if image_path and os.path.exists(image_path):
        try:
            img = Image.open(image_path)
            # 调整图片大小
            img_width = width - 120
            img_height = int(img.height * img_width / img.width)
            if img_height > 400:
                img_height = 400
            img = img.resize((img_width, img_height), Image.LANCZOS)
            
            # 粘贴到画布底部（无圆角，直接粘贴）
            x = 60
            y = height - img_height - 60
            canvas.paste(img, (x, y))
        except Exception as e:
            print(f"加载素材图片失败: {e}")
    
    # 保存
    canvas.save(output_path, quality=95)
    print(f"✅ 内容卡片已保存: {output_path}")

def main():
    # 输入参数
    output_dir = os.path.expanduser("~/.openclaw/media/xhs-final/")
    os.makedirs(output_dir, exist_ok=True)
    
    # 素材图片
    goji_img = os.path.expanduser("~/.openclaw/media/素材_枸杞.jpg")
    chrysanthemum_img = os.path.expanduser("~/.openclaw/media/素材_菊花.jpg")
    tea_img = os.path.expanduser("~/.openclaw/media/素材_养生茶.jpg")
    goji_tea_img = os.path.expanduser("~/.openclaw/media/素材_枸杞菊花茶_1.jpg")
    
    # 1. 创建封面
    create_cover_with_image(
        title="熬夜党必喝！",
        subtitle="3种茶护眼明目",
        image_path=tea_img,
        output_path=os.path.join(output_dir, "01_封面.png")
    )
    
    # 2. 原料展示卡片
    create_content_card_with_image(
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
    
    # 3. 制作方法卡片
    create_content_card_with_image(
        title="🍵 冲泡方法",
        content=[
            "Step 1: 材料洗净",
            "枸杞、菊花、决明子冲洗干净",
            "",
            "Step 2: 放入杯中",
            "所有材料放入养生壶/茶杯",
            "",
            "Step 3: 热水冲泡",
            "85℃热水焖泡5-8分钟即可"
        ],
        image_path=tea_img,
        output_path=os.path.join(output_dir, "03_方法.png")
    )
    
    # 4. 功效卡片
    create_content_card_with_image(
        title="✨ 护眼功效",
        content=[
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
    
    # 5. 温馨提示卡片
    create_content_card_with_image(
        title="💡 温馨提示",
        content=[
            "• 最佳饮用时间：下午3-5点",
            "",
            "• 每天一杯，坚持2周见效",
            "",
            "• 孕妇慎用决明子",
            "",
            "• 热敷温度不宜过高",
            "",
            "🌿 跟着赤兔，一起健康养生",
            "👆 点赞收藏，不迷路"
        ],
        image_path=None,
        output_path=os.path.join(output_dir, "05_提示.png")
    )
    
    print(f"\n✅ 所有卡片生成完成！保存位置: {output_dir}")

if __name__ == "__main__":
    main()
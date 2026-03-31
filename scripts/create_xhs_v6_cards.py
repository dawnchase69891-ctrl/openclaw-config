#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书养生配图 v6.0 - 完整内容结构
症状→经典→原料→方法→功效→提示
"""

from PIL import Image, ImageDraw, ImageFont
import os

WIDTH = 1242
HEIGHT = 1660

COLORS = {
    'primary': '#E85D04',
    'secondary': '#2D6A4F',
    'accent': '#F4A261',
    'text_dark': '#1A1A1A',
    'text_gray': '#4A4A4A',
    'text_light': '#FFFFFF',
    'bg_white': '#FFFFFF',
    'bg_cream': '#FFFBF5',
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

def create_card_1_symptoms(image_path, output_path):
    """卡片1：症状痛点封面"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    
    # 背景图占60%
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img_ratio = img.width / img.height
        target_height = int(HEIGHT * 0.6)
        target_width = WIDTH
        
        if img_ratio > target_width / target_height:
            new_width = target_width
            new_height = int(new_width / img_ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)
        else:
            new_height = target_height
            new_width = int(new_height * img_ratio)
        
        img = img.resize((WIDTH, target_height), Image.LANCZOS)
        canvas.paste(img, (0, 0))
    
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(90, bold=True)
    font_symptom = load_font(42)
    font_sub = load_font(36)
    
    # 大标题
    draw.text((50, int(HEIGHT * 0.65)), "熬夜党必喝！", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    
    # 症状列表
    symptoms = [
        "❌ 每天对着电脑8小时+",
        "❌ 眼睛干涩、酸胀、流泪",
        "❌ 视力模糊，看久了看不清",
        "❌ 眼疲劳，眼袋黑眼圈明显"
    ]
    y = int(HEIGHT * 0.78)
    for s in symptoms:
        draw.text((50, y), s, font=font_symptom, fill=hex_to_rgb(COLORS['text_gray']))
        y += 55
    
    # 底部
    draw.rectangle([0, HEIGHT-70, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, HEIGHT-50), "🌿 赤兔养生计划 · 护眼专题", font=font_sub, fill=hex_to_rgb(COLORS['text_light']))
    
    canvas.save(output_path, quality=98)
    print(f"✅ 卡片1-症状: {output_path}")

def create_card_2_classic(image_path, output_path):
    """卡片2：中医经典引用"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(52, bold=True)
    font_quote = load_font(36)
    font_source = load_font(28)
    font_theory = load_font(34)
    
    # 标题栏
    draw.rectangle([0, 0, WIDTH, 100], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, 30), "📜 中医怎么说？", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    y = 130
    
    # 经典引用1
    draw.text((50, y), "《本草纲目》记载：", font=font_source, fill=hex_to_rgb(COLORS['accent']))
    y += 45
    quote1 = "\"枸杞，补肾生精，养肝明目，"
    draw.text((70, y), quote1, font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 50
    draw.text((70, y), "坚精骨，去疲劳，令人长寿。\"", font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 70
    
    # 经典引用2
    draw.text((50, y), "《黄帝内经》云：", font=font_source, fill=hex_to_rgb(COLORS['accent']))
    y += 45
    draw.text((70, y), "\"肝开窍于目\"", font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 50
    draw.text((70, y), "\"肝受血而能视\"", font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 80
    
    # 中医理论
    draw.rectangle([40, y, WIDTH-40, y+180], fill=hex_to_rgb(COLORS['bg_white']))
    y += 20
    draw.text((60, y), "💡 中医理论", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 55
    theories = [
        "• 眼睛是肝的\"窗户\"",
        "• 肝血不足 → 眼睛干涩疲劳",
        "• 补肝养血 → 明目护眼"
    ]
    for t in theories:
        draw.text((60, y), t, font=font_theory, fill=hex_to_rgb(COLORS['text_gray']))
        y += 45
    
    # 底部图片
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((WIDTH-80, 350), Image.LANCZOS)
        canvas.paste(img, (40, HEIGHT-430))
        draw.rectangle([40, HEIGHT-430, WIDTH-40, HEIGHT-80], outline=hex_to_rgb(COLORS['accent']), width=2)
    
    canvas.save(output_path, quality=98)
    print(f"✅ 卡片2-经典: {output_path}")

def create_card_3_materials(image_path, output_path):
    """卡片3：原料准备"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(52, bold=True)
    font_item = load_font(38)
    font_desc = load_font(30)
    
    # 标题栏
    draw.rectangle([0, 0, WIDTH, 100], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, 30), "🌿 原料准备", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 材料列表
    materials = [
        ("枸杞 10g", "补肾生精，养肝明目", COLORS['primary']),
        ("菊花 5朵", "清肝明目，清热解毒", COLORS['accent']),
        ("决明子 5g", "清肝明目，润肠通便", COLORS['secondary']),
    ]
    
    y = 140
    for name, desc, color in materials:
        # 材料名
        draw.rectangle([50, y, WIDTH-50, y+80], fill=hex_to_rgb(COLORS['bg_white']))
        draw.text((70, y+10), name, font=font_item, fill=hex_to_rgb(color))
        draw.text((70, y+50), desc, font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 100
    
    # 选购建议
    y += 20
    draw.text((50, y), "💡 选购建议", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 60
    tips = [
        "枸杞：选宁夏中宁枸杞，颜色暗红",
        "菊花：选胎菊或杭白菊，花朵完整",
        "决明子：选颗粒饱满、无杂质"
    ]
    for t in tips:
        draw.text((50, y), f"• {t}", font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 45
    
    # 底部图片
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((WIDTH-80, 320), Image.LANCZOS)
        canvas.paste(img, (40, HEIGHT-400))
    
    canvas.save(output_path, quality=98)
    print(f"✅ 卡片3-原料: {output_path}")

def create_card_4_method(image_path, output_path):
    """卡片4：制作方法"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    
    # 左侧图片
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((int(WIDTH*0.45), HEIGHT), Image.LANCZOS)
        canvas.paste(img, (0, 0))
    
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(48, bold=True)
    font_step = load_font(36)
    font_tip = load_font(30)
    
    # 右侧内容区
    x = int(WIDTH * 0.5)
    
    # 标题
    draw.text((x, 50), "🍵 制作方法", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    
    # 步骤
    steps = [
        ("Step 1", "材料洗净", "枸杞、菊花、决明子冲洗干净"),
        ("Step 2", "放入杯中", "所有材料放入养生壶或茶杯"),
        ("Step 3", "热水冲泡", "85℃热水焖泡5-8分钟"),
    ]
    
    y = 130
    for num, title, desc in steps:
        draw.ellipse([x, y, x+50, y+50], fill=hex_to_rgb(COLORS['accent']))
        draw.text((x+12, y+8), num[-1], font=load_font(28, bold=True), fill=hex_to_rgb(COLORS['text_dark']))
        draw.text((x+70, y+5), title, font=font_step, fill=hex_to_rgb(COLORS['text_dark']))
        draw.text((x+70, y+45), desc, font=font_tip, fill=hex_to_rgb(COLORS['text_gray']))
        y += 100
    
    # 小贴士
    y += 30
    draw.rectangle([x-10, y, WIDTH-30, y+150], fill=hex_to_rgb(COLORS['bg_cream']))
    draw.text((x+10, y+15), "💡 小贴士", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 60
    tips = ["可反复冲泡2-3次", "最佳饮用时间：下午3-5点"]
    for t in tips:
        draw.text((x+10, y), f"• {t}", font=font_tip, fill=hex_to_rgb(COLORS['text_gray']))
        y += 40
    
    canvas.save(output_path, quality=98)
    print(f"✅ 卡片4-方法: {output_path}")

def create_card_5_effect(image_path, output_path):
    """卡片5：功效说明"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    
    # 背景图
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        canvas.paste(img, (0, 0))
        
        # 渐变遮罩
        for y in range(int(HEIGHT*0.3), HEIGHT):
            alpha = int(200 * (y - HEIGHT*0.3) / (HEIGHT*0.7))
            for x in range(WIDTH):
                pixel = canvas.getpixel((x, y))
                new_color = tuple(int(pixel[i] * (255-alpha)/255 + int(hex_to_rgb(COLORS['bg_white'])[i]) * alpha/255) for i in range(3))
                canvas.putpixel((x, y), new_color)
    
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(52, bold=True)
    font_effect = load_font(36)
    font_result = load_font(32)
    
    # 标题
    draw.text((50, int(HEIGHT*0.35)), "✨ 护眼功效", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    
    # 三大功效
    effects = [
        ("清肝明目", "缓解眼干、眼涩、眼疲劳"),
        ("滋补肝肾", "改善视力模糊、夜盲症状"),
        ("抗氧化", "延缓眼睛衰老，保护视网膜"),
    ]
    
    y = int(HEIGHT*0.45)
    for title, desc in effects:
        draw.text((50, y), f"✅ {title}", font=font_effect, fill=hex_to_rgb(COLORS['text_dark']))
        draw.text((80, y+45), desc, font=font_result, fill=hex_to_rgb(COLORS['text_gray']))
        y += 100
    
    # 效果时间线
    y += 30
    draw.text((50, y), "📈 坚持喝的效果", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 55
    timeline = [
        "1周 → 眼睛不那么干了",
        "2周 → 眼疲劳明显缓解",
        "1月 → 视力更清晰"
    ]
    for t in timeline:
        draw.text((50, y), t, font=font_result, fill=hex_to_rgb(COLORS['text_gray']))
        y += 40
    
    canvas.save(output_path, quality=98)
    print(f"✅ 卡片5-功效: {output_path}")

def create_card_6_tips(output_path):
    """卡片6：温馨提示"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(48, bold=True)
    font_content = load_font(34)
    font_small = load_font(28)
    
    # 标题栏
    draw.rectangle([0, 0, WIDTH, 100], fill=hex_to_rgb(COLORS['primary']))
    draw.text((50, 30), "💡 温馨提示", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 饮用建议
    y = 140
    draw.rectangle([40, y, WIDTH-40, y+200], fill=hex_to_rgb(COLORS['bg_white']))
    draw.text((60, y+15), "✅ 饮用建议", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 60
    tips = [
        "最佳时间：下午3-5点",
        "每天一杯，坚持2周见效",
        "可搭配热敷眼睛效果更佳"
    ]
    for t in tips:
        draw.text((60, y), f"• {t}", font=font_content, fill=hex_to_rgb(COLORS['text_gray']))
        y += 45
    
    # 禁忌人群
    y = 380
    draw.rectangle([40, y, WIDTH-40, y+200], fill=hex_to_rgb('#FFF5F5']))
    draw.text((60, y+15), "❌ 禁忌人群", font=font_title, fill=hex_to_rgb('#D32F2F'))
    y += 60
    forbidden = [
        "孕妇慎用决明子",
        "脾胃虚寒者不宜空腹饮用",
        "感冒发烧时暂停饮用"
    ]
    for t in forbidden:
        draw.text((60, y), f"• {t}", font=font_content, fill=hex_to_rgb(COLORS['text_gray']))
        y += 45
    
    # 互动引导
    y = 620
    draw.text((50, y), "💬 互动引导", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 55
    interactions = [
        "👆 点赞收藏，不迷路",
        "💬 评论区告诉我你的养生心得",
        "🌿 关注赤兔，一起健康养生"
    ]
    for t in interactions:
        draw.text((50, y), t, font=font_content, fill=hex_to_rgb(COLORS['text_dark']))
        y += 45
    
    # 标签
    y += 50
    tags = "#赤兔养生计划 #职场养生 #中医养生 #护眼 #熬夜党必备"
    draw.text((50, y), tags, font=font_small, fill=hex_to_rgb(COLORS['accent']))
    
    # 底部品牌
    draw.rectangle([0, HEIGHT-100, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, HEIGHT-70), "🌿 赤兔养生计划 · 跟着赤兔，一起健康养生", font=font_content, fill=hex_to_rgb(COLORS['text_light']))
    
    canvas.save(output_path, quality=98)
    print(f"✅ 卡片6-提示: {output_path}")

def main():
    output_dir = os.path.expanduser("~/.openclaw/media/xhs-v6/")
    os.makedirs(output_dir, exist_ok=True)
    
    goji_img = os.path.expanduser("~/.openclaw/media/素材_枸杞.jpg")
    chrysanthemum_img = os.path.expanduser("~/.openclaw/media/素材_菊花.jpg")
    tea_img = os.path.expanduser("~/.openclaw/media/素材_养生茶.jpg")
    
    print("🎨 生成完整内容配图（6张）...\n")
    
    create_card_1_symptoms(tea_img, os.path.join(output_dir, "01_症状痛点.png"))
    create_card_2_classic(goji_img, os.path.join(output_dir, "02_中医经典.png"))
    create_card_3_materials(goji_img, os.path.join(output_dir, "03_原料准备.png"))
    create_card_4_method(tea_img, os.path.join(output_dir, "04_制作方法.png"))
    create_card_5_effect(chrysanthemum_img, os.path.join(output_dir, "05_功效说明.png"))
    create_card_6_tips(os.path.join(output_dir, "06_温馨提示.png"))
    
    print(f"\n✅ 完成！位置: {output_dir}")

if __name__ == "__main__":
    main()
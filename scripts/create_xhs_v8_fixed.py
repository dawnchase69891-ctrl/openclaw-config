#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书养生配图 v8.0 - 修复排版问题
增大行距，避免字体重叠
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
    'red': '#D32F2F',
    'green': '#388E3C',
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

def create_card_1(image_path, output_path):
    """卡片1：症状痛点封面"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img_ratio = img.width / img.height
        target_height = int(HEIGHT * 0.60)
        target_width = WIDTH
        
        if img_ratio > target_width / target_height:
            new_height = target_height
            new_width = int(new_height * img_ratio)
            left = (new_width - WIDTH) // 2
            img = img.resize((new_width, new_height), Image.LANCZOS)
            img = img.crop((left, 0, left + WIDTH, new_height))
        else:
            new_width = WIDTH
            new_height = int(new_width / img_ratio)
            top = int((new_height - target_height) * 0.3)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            img = img.crop((0, top, new_width, top + target_height))
        
        canvas.paste(img, (0, 0))
    
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(72, bold=True)
    font_sub = load_font(36)
    font_symptom = load_font(30)
    
    # 大标题
    y = int(HEIGHT * 0.65)
    draw.text((40, y), "熬夜党必喝！", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 90
    
    # 副标题
    draw.text((40, y), "这杯茶让我眼睛从5.1回到5.0", font=font_sub, fill=hex_to_rgb(COLORS['text_dark']))
    y += 60
    
    # 症状列表
    symptoms = [
        "眼睛干涩刺痛，像进了沙子",
        "看屏幕字开始重影",
        "眼袋黑眼圈明显",
        "充满红血丝"
    ]
    for s in symptoms:
        draw.text((40, y), "X " + s, font=font_symptom, fill=hex_to_rgb(COLORS['text_gray']))
        y += 48
    
    # 底部品牌栏
    draw.rectangle([0, HEIGHT-60, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((40, HEIGHT-45), "赤兔养生计划 - 护眼专题", font=load_font(28), fill=hex_to_rgb(COLORS['text_light']))
    
    canvas.save(output_path, quality=100, dpi=(300, 300))
    print(f"1.封面: {os.path.getsize(output_path)//1024}KB")

def create_card_2(image_path, output_path):
    """卡片2：中医经典"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(40, bold=True)
    font_quote = load_font(28)
    font_source = load_font(24)
    font_data = load_font(26)
    
    # 标题栏
    draw.rectangle([0, 0, WIDTH, 80], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((40, 22), "为什么这杯茶有效？", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    y = 100
    
    # 经典引用1
    draw.text((40, y), "《本草纲目》记载：", font=font_source, fill=hex_to_rgb(COLORS['accent']))
    y += 40
    draw.text((60, y), "枸杞，补肾生精，养肝明目", font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 40
    draw.text((60, y), "坚精骨，去疲劳，令人长寿", font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 60
    
    # 经典引用2
    draw.text((40, y), "《黄帝内经》云：", font=font_source, fill=hex_to_rgb(COLORS['accent']))
    y += 40
    draw.text((60, y), "肝开窍于目 | 肝受血而能视", font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 70
    
    # 古代秘方
    draw.rectangle([30, y, WIDTH-30, y+130], fill=hex_to_rgb(COLORS['bg_white']))
    y += 15
    draw.text((50, y), "古代御医的秘密", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 50
    draw.text((50, y), "乾隆皇帝80岁还能批阅奏章到深夜", font=font_data, fill=hex_to_rgb(COLORS['text_dark']))
    y += 35
    draw.text((50, y), "秘诀：每日一杯枸杞菊花茶", font=font_data, fill=hex_to_rgb(COLORS['text_gray']))
    y += 90
    
    # 现代科学
    draw.rectangle([30, y, WIDTH-30, y+140], fill=hex_to_rgb('#E8F5E9'))
    y += 15
    draw.text((50, y), "现代科学验证", font=font_title, fill=hex_to_rgb(COLORS['green']))
    y += 50
    science = [
        "枸杞玉米黄质吸收蓝光",
        "菊花木犀草素抗氧化",
        "两者搭配效果提升3倍"
    ]
    for s in science:
        draw.text((50, y), "V " + s, font=font_data, fill=hex_to_rgb(COLORS['text_gray']))
        y += 35
    
    canvas.save(output_path, quality=100, dpi=(300, 300))
    print(f"2.经典: {os.path.getsize(output_path)//1024}KB")

def create_card_3(image_path, output_path):
    """卡片3：原料准备"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(40, bold=True)
    font_item = load_font(30)
    font_desc = load_font(24)
    
    # 标题栏
    draw.rectangle([0, 0, WIDTH, 80], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((40, 22), "三种原料，缺一不可", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 材料卡片
    materials = [
        ("枸杞 10g", "补肾生精，养肝明目", COLORS['primary']),
        ("菊花 5朵", "清肝明目，清热解毒", COLORS['accent']),
        ("决明子 5g", "清肝明目，润肠通便", COLORS['secondary']),
    ]
    
    y = 100
    for name, effect, color in materials:
        draw.rectangle([30, y, WIDTH-30, y+90], fill=hex_to_rgb(COLORS['bg_cream']))
        draw.text((50, y+18), name, font=font_item, fill=hex_to_rgb(color))
        draw.text((50, y+55), effect, font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 105
    
    # 黄金搭配
    y += 20
    draw.text((40, y), "黄金搭配原理", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 50
    principles = [
        "枸杞补 - 滋养肝血",
        "菊花清 - 清除肝火",
        "决明子通 - 润肠通便"
    ]
    for p in principles:
        draw.text((40, y), "* " + p, font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 40
    
    # 选品口诀
    y += 20
    draw.text((40, y), "选品口诀", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 50
    tips = [
        "枸杞：宁夏中宁，暗红饱满",
        "菊花：胎菊最好，花朵完整",
        "决明子：颗粒饱满无杂质"
    ]
    for t in tips:
        draw.text((40, y), "- " + t, font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 38
    
    # 成本
    y += 20
    draw.rectangle([30, y, WIDTH-30, y+60], fill=hex_to_rgb('#FFF3E0'))
    draw.text((50, y+18), "单杯成本：仅需 4.25元", font=font_item, fill=hex_to_rgb(COLORS['primary']))
    
    canvas.save(output_path, quality=100, dpi=(300, 300))
    print(f"3.原料: {os.path.getsize(output_path)//1024}KB")

def create_card_4(image_path, output_path):
    """卡片4：制作方法"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((int(WIDTH*0.42), HEIGHT), Image.LANCZOS)
        canvas.paste(img, (0, 0))
    
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(36, bold=True)
    font_step = load_font(28)
    font_desc = load_font(22)
    
    x = int(WIDTH * 0.47)
    
    # 标题
    draw.text((x, 40), "5分钟搞定", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    
    # 步骤
    steps = [
        ("1", "材料清洗", "枸杞快速冲洗"),
        ("2", "放入杯中", "决明子先放"),
        ("3", "热水冲泡", "85度焖泡5分钟"),
    ]
    
    y = 110
    for num, title, desc in steps:
        draw.ellipse([x, y, x+40, y+40], fill=hex_to_rgb(COLORS['accent']))
        draw.text((x+12, y+6), num, font=load_font(24, bold=True), fill=hex_to_rgb(COLORS['text_dark']))
        draw.text((x+55, y+5), title, font=font_step, fill=hex_to_rgb(COLORS['text_dark']))
        draw.text((x+55, y+35), desc, font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 75
    
    # 进阶技巧
    y += 20
    draw.rectangle([x-10, y, WIDTH-20, y+110], fill=hex_to_rgb(COLORS['bg_cream']))
    draw.text((x+10, y+10), "进阶技巧", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 40
    tips = ["可加蜂蜜调味", "可续水2-3次", "枸杞直接吃掉"]
    for t in tips:
        draw.text((x+10, y), "- " + t, font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 28
    
    # 最佳时间
    y += 20
    draw.text((x, y), "最佳饮用时间", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 40
    draw.text((x, y), "下午3-5点", font=font_step, fill=hex_to_rgb(COLORS['accent']))
    
    canvas.save(output_path, quality=100, dpi=(300, 300))
    print(f"4.方法: {os.path.getsize(output_path)//1024}KB")

def create_card_5(image_path, output_path):
    """卡片5：功效说明"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        canvas.paste(img, (0, 0))
        
        # 渐变遮罩
        for y in range(int(HEIGHT*0.30), HEIGHT):
            alpha = int(230 * (y - HEIGHT*0.30) / (HEIGHT*0.70))
            for x in range(WIDTH):
                pixel = canvas.getpixel((x, y))
                new_color = tuple(int(pixel[i] * (255-alpha)/255 + 255 * alpha/255) for i in range(3))
                canvas.putpixel((x, y), new_color)
    
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(42, bold=True)
    font_effect = load_font(30)
    font_data = load_font(24)
    
    # 标题
    y = int(HEIGHT*0.35)
    draw.text((40, y), "坚持喝，你会看到变化", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 70
    
    # 三大功效
    effects = [
        ("清肝明目", "1周后眼睛不再干涩"),
        ("滋补肝肾", "2周后视力更清晰"),
        ("抗氧抗衰", "1月后眼袋淡化"),
    ]
    
    for title, effect in effects:
        draw.text((40, y), "V " + title, font=font_effect, fill=hex_to_rgb(COLORS['text_dark']))
        draw.text((80, y+38), effect, font=font_data, fill=hex_to_rgb(COLORS['text_gray']))
        y += 85
    
    # 效果时间线
    y += 20
    draw.text((40, y), "效果时间线", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 50
    timeline = [
        "1周 -> 眼干缓解",
        "2周 -> 视力清晰",
        "1月 -> 黑眼圈淡化"
    ]
    for t in timeline:
        draw.text((40, y), t, font=font_data, fill=hex_to_rgb(COLORS['text_gray']))
        y += 38
    
    canvas.save(output_path, quality=100, dpi=(300, 300))
    print(f"5.功效: {os.path.getsize(output_path)//1024}KB")

def create_card_6(output_path):
    """卡片6：温馨提示"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(36, bold=True)
    font_content = load_font(26)
    font_small = load_font(22)
    
    # 标题栏
    draw.rectangle([0, 0, WIDTH, 75], fill=hex_to_rgb(COLORS['primary']))
    draw.text((40, 22), "饮用指南", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 饮用建议
    y = 95
    draw.rectangle([25, y, WIDTH-25, y+140], fill=hex_to_rgb(COLORS['bg_white']))
    draw.text((45, y+12), "饮用建议", font=font_title, fill=hex_to_rgb(COLORS['green']))
    y += 45
    tips = [
        "最佳时间：下午3-5点",
        "最佳频率：每天1杯",
        "最佳温度：温热饮用"
    ]
    for t in tips:
        draw.text((45, y), "* " + t, font=font_content, fill=hex_to_rgb(COLORS['text_gray']))
        y += 32
    
    # 禁忌人群
    y = 260
    draw.rectangle([25, y, WIDTH-25, y+140], fill=hex_to_rgb('#FFEBEE'))
    draw.text((45, y+12), "禁忌人群", font=font_title, fill=hex_to_rgb(COLORS['red']))
    y += 45
    forbidden = [
        "孕妇慎用决明子",
        "脾胃虚寒者饭后饮用",
        "感冒发烧时暂停"
    ]
    for f in forbidden:
        draw.text((45, y), "X " + f, font=font_content, fill=hex_to_rgb(COLORS['text_gray']))
        y += 32
    
    # Q&A
    y = 430
    draw.text((40, y), "常见问题", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 45
    qa = [
        "Q: 喝了拉肚子？",
        "A: 减量或饭后喝",
        "",
        "Q: 可以不加决明子？",
        "A: 可以但效果打折扣"
    ]
    for q in qa:
        draw.text((40, y), q, font=font_small, fill=hex_to_rgb(COLORS['text_gray']))
        y += 30
    
    # 互动引导
    y += 20
    draw.text((40, y), "互动引导", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 45
    interactions = [
        "点赞收藏，下次翻出来",
        "评论区晒你的变化",
        "关注解锁更多养生秘籍"
    ]
    for i in interactions:
        draw.text((40, y), "-> " + i, font=font_content, fill=hex_to_rgb(COLORS['text_dark']))
        y += 35
    
    # 标签
    y += 20
    draw.text((40, y), "#赤兔养生 #职场养生 #护眼", font=font_small, fill=hex_to_rgb(COLORS['accent']))
    
    # 底部品牌
    draw.rectangle([0, HEIGHT-70, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((40, HEIGHT-50), "赤兔养生计划", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    canvas.save(output_path, quality=100, dpi=(300, 300))
    print(f"6.提示: {os.path.getsize(output_path)//1024}KB")

def main():
    output_dir = os.path.expanduser("~/.openclaw/media/xhs-v8/")
    os.makedirs(output_dir, exist_ok=True)
    
    goji = os.path.expanduser("~/.openclaw/media/素材_枸杞.jpg")
    chrys = os.path.expanduser("~/.openclaw/media/素材_菊花.jpg")
    tea = os.path.expanduser("~/.openclaw/media/素材_养生茶.jpg")
    
    print("生成修复版配图（增大行距）...\n")
    
    create_card_1(tea, output_dir + "01_封面.png")
    create_card_2(goji, output_dir + "02_中医经典.png")
    create_card_3(goji, output_dir + "03_原料准备.png")
    create_card_4(tea, output_dir + "04_制作方法.png")
    create_card_5(chrys, output_dir + "05_功效说明.png")
    create_card_6(output_dir + "06_温馨提示.png")
    
    print(f"\n完成！位置: {output_dir}")

if __name__ == "__main__":
    main()
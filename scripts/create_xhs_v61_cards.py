#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书养生配图 v6.1 - 完整内容结构
症状-经典-原料-方法-功效-提示
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
    'bg_red': '#FFF5F5',
    'red': '#D32F2F',
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
    """症状痛点封面"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((WIDTH, int(HEIGHT * 0.6)), Image.LANCZOS)
        canvas.paste(img, (0, 0))
    
    draw = ImageDraw.Draw(canvas)
    font_title = load_font(90, bold=True)
    font_symptom = load_font(42)
    font_sub = load_font(36)
    
    draw.text((50, int(HEIGHT * 0.65)), "熬夜党必喝！", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    
    symptoms = [
        "每天对着电脑8小时+",
        "眼睛干涩、酸胀、流泪",
        "视力模糊，看久了看不清",
        "眼疲劳，眼袋黑眼圈明显"
    ]
    y = int(HEIGHT * 0.78)
    for s in symptoms:
        draw.text((50, y), "X " + s, font=font_symptom, fill=hex_to_rgb(COLORS['text_gray']))
        y += 55
    
    draw.rectangle([0, HEIGHT-70, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, HEIGHT-50), "赤兔养生计划 - 护眼专题", font=font_sub, fill=hex_to_rgb(COLORS['text_light']))
    
    canvas.save(output_path, quality=98)
    print(f"1.症状: {output_path}")

def create_card_2(image_path, output_path):
    """中医经典"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(52, bold=True)
    font_quote = load_font(36)
    font_source = load_font(28)
    font_theory = load_font(34)
    
    draw.rectangle([0, 0, WIDTH, 100], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, 30), "中医怎么说？", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    y = 130
    draw.text((50, y), "《本草纲目》记载：", font=font_source, fill=hex_to_rgb(COLORS['accent']))
    y += 45
    draw.text((70, y), "枸杞，补肾生精，养肝明目，", font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 50
    draw.text((70, y), "坚精骨，去疲劳，令人长寿。", font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 70
    
    draw.text((50, y), "《黄帝内经》云：", font=font_source, fill=hex_to_rgb(COLORS['accent']))
    y += 45
    draw.text((70, y), "肝开窍于目", font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 50
    draw.text((70, y), "肝受血而能视", font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 80
    
    draw.rectangle([40, y, WIDTH-40, y+180], fill=hex_to_rgb(COLORS['bg_white']))
    y += 20
    draw.text((60, y), "中医理论", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 55
    for t in ["眼睛是肝的窗户", "肝血不足 - 眼睛干涩疲劳", "补肝养血 - 明目护眼"]:
        draw.text((60, y), "* " + t, font=font_theory, fill=hex_to_rgb(COLORS['text_gray']))
        y += 45
    
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((WIDTH-80, 350), Image.LANCZOS)
        canvas.paste(img, (40, HEIGHT-430))
    
    canvas.save(output_path, quality=98)
    print(f"2.经典: {output_path}")

def create_card_3(image_path, output_path):
    """原料准备"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(52, bold=True)
    font_item = load_font(38)
    font_desc = load_font(30)
    
    draw.rectangle([0, 0, WIDTH, 100], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, 30), "原料准备", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    materials = [
        ("枸杞 10g", "补肾生精，养肝明目"),
        ("菊花 5朵", "清肝明目，清热解毒"),
        ("决明子 5g", "清肝明目，润肠通便"),
    ]
    
    y = 140
    for name, desc in materials:
        draw.rectangle([50, y, WIDTH-50, y+80], fill=hex_to_rgb(COLORS['bg_white']))
        draw.text((70, y+10), name, font=font_item, fill=hex_to_rgb(COLORS['primary']))
        draw.text((70, y+50), desc, font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 100
    
    y += 20
    draw.text((50, y), "选购建议", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 60
    for t in ["枸杞：选宁夏中宁枸杞", "菊花：选胎菊或杭白菊", "决明子：选颗粒饱满"]:
        draw.text((50, y), "* " + t, font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 45
    
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((WIDTH-80, 320), Image.LANCZOS)
        canvas.paste(img, (40, HEIGHT-400))
    
    canvas.save(output_path, quality=98)
    print(f"3.原料: {output_path}")

def create_card_4(image_path, output_path):
    """制作方法"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((int(WIDTH*0.45), HEIGHT), Image.LANCZOS)
        canvas.paste(img, (0, 0))
    
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(48, bold=True)
    font_step = load_font(36)
    font_tip = load_font(30)
    
    x = int(WIDTH * 0.5)
    draw.text((x, 50), "制作方法", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    
    steps = [
        ("Step 1", "材料洗净", "枸杞、菊花冲洗干净"),
        ("Step 2", "放入杯中", "所有材料放入茶杯"),
        ("Step 3", "热水冲泡", "85度热水焖泡5-8分钟"),
    ]
    
    y = 130
    for num, title, desc in steps:
        draw.ellipse([x, y, x+50, y+50], fill=hex_to_rgb(COLORS['accent']))
        draw.text((x+15, y+10), num[-1], font=load_font(28, bold=True), fill=hex_to_rgb(COLORS['text_dark']))
        draw.text((x+70, y+5), title, font=font_step, fill=hex_to_rgb(COLORS['text_dark']))
        draw.text((x+70, y+45), desc, font=font_tip, fill=hex_to_rgb(COLORS['text_gray']))
        y += 100
    
    y += 30
    draw.rectangle([x-10, y, WIDTH-30, y+150], fill=hex_to_rgb(COLORS['bg_cream']))
    draw.text((x+10, y+15), "小贴士", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 60
    for t in ["可反复冲泡2-3次", "最佳饮用：下午3-5点"]:
        draw.text((x+10, y), "* " + t, font=font_tip, fill=hex_to_rgb(COLORS['text_gray']))
        y += 40
    
    canvas.save(output_path, quality=98)
    print(f"4.方法: {output_path}")

def create_card_5(image_path, output_path):
    """功效说明"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        canvas.paste(img, (0, 0))
        
        for y in range(int(HEIGHT*0.3), HEIGHT):
            alpha = int(200 * (y - HEIGHT*0.3) / (HEIGHT*0.7))
            for x in range(WIDTH):
                pixel = canvas.getpixel((x, y))
                new_color = tuple(int(pixel[i] * (255-alpha)/255 + 255 * alpha/255) for i in range(3))
                canvas.putpixel((x, y), new_color)
    
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(52, bold=True)
    font_effect = load_font(36)
    font_result = load_font(32)
    
    draw.text((50, int(HEIGHT*0.35)), "护眼功效", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    
    effects = [
        ("清肝明目", "缓解眼干、眼涩、眼疲劳"),
        ("滋补肝肾", "改善视力模糊、夜盲症状"),
        ("抗氧化", "延缓眼睛衰老，保护视网膜"),
    ]
    
    y = int(HEIGHT*0.45)
    for title, desc in effects:
        draw.text((50, y), "V " + title, font=font_effect, fill=hex_to_rgb(COLORS['text_dark']))
        draw.text((80, y+45), desc, font=font_result, fill=hex_to_rgb(COLORS['text_gray']))
        y += 100
    
    y += 30
    draw.text((50, y), "坚持喝的效果", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 55
    for t in ["1周 - 眼睛不那么干了", "2周 - 眼疲劳明显缓解", "1月 - 视力更清晰"]:
        draw.text((50, y), t, font=font_result, fill=hex_to_rgb(COLORS['text_gray']))
        y += 40
    
    canvas.save(output_path, quality=98)
    print(f"5.功效: {output_path}")

def create_card_6(output_path):
    """温馨提示"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(48, bold=True)
    font_content = load_font(34)
    font_small = load_font(28)
    
    draw.rectangle([0, 0, WIDTH, 100], fill=hex_to_rgb(COLORS['primary']))
    draw.text((50, 30), "温馨提示", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    y = 140
    draw.rectangle([40, y, WIDTH-40, y+200], fill=hex_to_rgb(COLORS['bg_white']))
    draw.text((60, y+15), "饮用建议", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 60
    for t in ["最佳时间：下午3-5点", "每天一杯，坚持2周见效", "可搭配热敷眼睛效果更佳"]:
        draw.text((60, y), "* " + t, font=font_content, fill=hex_to_rgb(COLORS['text_gray']))
        y += 45
    
    y = 380
    draw.rectangle([40, y, WIDTH-40, y+200], fill=hex_to_rgb(COLORS['bg_red']))
    draw.text((60, y+15), "禁忌人群", font=font_title, fill=hex_to_rgb(COLORS['red']))
    y += 60
    for t in ["孕妇慎用决明子", "脾胃虚寒者不宜空腹饮用", "感冒发烧时暂停饮用"]:
        draw.text((60, y), "* " + t, font=font_content, fill=hex_to_rgb(COLORS['text_gray']))
        y += 45
    
    y = 620
    draw.text((50, y), "互动引导", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 55
    for t in ["点赞收藏，不迷路", "评论区告诉我你的养生心得", "关注赤兔，一起健康养生"]:
        draw.text((50, y), t, font=font_content, fill=hex_to_rgb(COLORS['text_dark']))
        y += 45
    
    y += 50
    draw.text((50, y), "#赤兔养生计划 #职场养生 #护眼", font=font_small, fill=hex_to_rgb(COLORS['accent']))
    
    draw.rectangle([0, HEIGHT-100, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, HEIGHT-70), "赤兔养生计划 - 跟着赤兔，一起健康养生", font=font_content, fill=hex_to_rgb(COLORS['text_light']))
    
    canvas.save(output_path, quality=98)
    print(f"6.提示: {output_path}")

def main():
    output_dir = os.path.expanduser("~/.openclaw/media/xhs-v6/")
    os.makedirs(output_dir, exist_ok=True)
    
    goji = os.path.expanduser("~/.openclaw/media/素材_枸杞.jpg")
    chrys = os.path.expanduser("~/.openclaw/media/素材_菊花.jpg")
    tea = os.path.expanduser("~/.openclaw/media/素材_养生茶.jpg")
    
    print("生成6张配图...")
    
    create_card_1(tea, output_dir + "01_症状痛点.png")
    create_card_2(goji, output_dir + "02_中医经典.png")
    create_card_3(goji, output_dir + "03_原料准备.png")
    create_card_4(tea, output_dir + "04_制作方法.png")
    create_card_5(chrys, output_dir + "05_功效说明.png")
    create_card_6(output_dir + "06_温馨提示.png")
    
    print("完成！")

if __name__ == "__main__":
    main()
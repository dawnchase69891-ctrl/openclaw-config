#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书广告级配图 v10.0 - 专业设计
等比例拉伸，美观大气，易阅读
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

WIDTH = 1242
HEIGHT = 1660

# 专业配色（莫兰迪色系）
COLORS = {
    'primary': '#C67B4E',       # 暖棕
    'secondary': '#5B8A72',     # 森绿
    'accent': '#D4A574',        # 金棕
    'text_dark': '#2C2C2C',
    'text_gray': '#5A5A5A',
    'text_light': '#FFFFFF',
    'bg_cream': '#FAF7F2',
    'bg_white': '#FFFFFF',
    'overlay': '#00000080',
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

def fit_image_proportional(img, target_width, target_height):
    """
    等比例缩放图片，填满目标区域
    超出部分会被裁剪，但图片不变形
    """
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height
    
    # 计算缩放后的尺寸（保持比例，至少填满一边）
    if img_ratio > target_ratio:
        # 图片更宽，以高度为准
        new_height = target_height
        new_width = int(new_height * img_ratio)
    else:
        # 图片更高，以宽度为准
        new_width = target_width
        new_height = int(new_width / img_ratio)
    
    # 高质量缩放
    img_resized = img.resize((new_width, new_height), Image.LANCZOS)
    
    # 居中裁剪
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    
    # 如果图片太小，扩展画布
    if new_width < target_width:
        canvas = Image.new('RGB', (target_width, target_height), (250, 247, 242))
        x = (target_width - new_width) // 2
        canvas.paste(img_resized, (x, 0))
        return canvas
    elif new_height < target_height:
        canvas = Image.new('RGB', (target_width, target_height), (250, 247, 242))
        y = (target_height - new_height) // 2
        canvas.paste(img_resized, (0, y))
        return canvas
    else:
        return img_resized.crop((left, top, left + target_width, top + target_height))

def add_gradient_overlay(canvas, start_y_ratio=0.5, end_alpha=180):
    """添加渐变遮罩，让文字清晰"""
    width, height = canvas.size
    start_y = int(height * start_y_ratio)
    
    for y in range(start_y, height):
        alpha = int(end_alpha * (y - start_y) / (height - start_y))
        for x in range(width):
            pixel = canvas.getpixel((x, y))
            new_color = tuple(int(pixel[i] * (255 - alpha) / 255) for i in range(3))
            canvas.putpixel((x, y), new_color)
    
    return canvas

def create_cover(image_path, output_path):
    """封面：大图背景 + 精致排版"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    
    # 背景图（等比例缩放填满）
    if os.path.exists(image_path):
        img = Image.open(image_path)
        bg = fit_image_proportional(img, WIDTH, int(HEIGHT * 0.65))
        canvas.paste(bg, (0, 0))
        
        # 渐变过渡
        for y in range(int(HEIGHT * 0.55), int(HEIGHT * 0.65)):
            alpha = int(255 * (y - HEIGHT * 0.55) / (HEIGHT * 0.1))
            for x in range(WIDTH):
                pixel = canvas.getpixel((x, y))
                bg_color = hex_to_rgb(COLORS['bg_cream'])
                new_color = tuple(int(pixel[i] * (255 - alpha) / 255 + bg_color[i] * alpha / 255) for i in range(3))
                canvas.putpixel((x, y), new_color)
    
    draw = ImageDraw.Draw(canvas)
    
    # 字体
    font_title = load_font(68, bold=True)
    font_sub = load_font(34)
    font_text = load_font(28)
    
    # 标题区
    y = int(HEIGHT * 0.68)
    draw.text((50, y), "熬夜党必喝！", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 85
    
    draw.text((50, y), "这杯茶让我眼睛从5.1回到5.0", font=font_sub, fill=hex_to_rgb(COLORS['text_dark']))
    y += 60
    
    # 症状列表（带图标）
    symptoms = [
        ("X", "眼睛干涩刺痛"),
        ("X", "看屏幕字重影"),
        ("X", "眼袋黑眼圈明显"),
        ("X", "红血丝布满眼睛"),
    ]
    
    for icon, text in symptoms:
        draw.text((50, y), icon, font=font_text, fill=hex_to_rgb(COLORS['primary']))
        draw.text((85, y), text, font=font_text, fill=hex_to_rgb(COLORS['text_gray']))
        y += 42
    
    # 底部品牌栏
    draw.rectangle([0, HEIGHT-70, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, HEIGHT-48), "赤兔养生计划 · 护眼专题", font=load_font(26), fill=hex_to_rgb(COLORS['text_light']))
    
    canvas.save(output_path, quality=100, dpi=(300, 300))
    print(f"1.封面: {os.path.getsize(output_path)//1024}KB")

def create_classic(output_path):
    """中医经典：纯文字排版"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(38, bold=True)
    font_quote = load_font(26)
    font_source = load_font(22)
    font_text = load_font(24)
    
    # 顶部装饰
    draw.rectangle([0, 0, WIDTH, 70], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, 20), "为什么这杯茶有效？", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    y = 100
    
    # 引用卡片1
    draw.rectangle([30, y, WIDTH-30, y+150], fill=hex_to_rgb(COLORS['bg_white']), outline=hex_to_rgb(COLORS['accent']), width=2)
    y += 20
    draw.text((50, y), "《本草纲目》", font=font_source, fill=hex_to_rgb(COLORS['accent']))
    y += 35
    draw.text((50, y), "枸杞，补肾生精，养肝明目", font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 38
    draw.text((50, y), "坚精骨，去疲劳，令人长寿", font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 50
    
    # 引用卡片2
    draw.rectangle([30, y, WIDTH-30, y+120], fill=hex_to_rgb(COLORS['bg_white']), outline=hex_to_rgb(COLORS['secondary']), width=2)
    y += 20
    draw.text((50, y), "《黄帝内经》", font=font_source, fill=hex_to_rgb(COLORS['secondary']))
    y += 35
    draw.text((50, y), "肝开窍于目 | 肝受血而能视", font=font_quote, fill=hex_to_rgb(COLORS['text_dark']))
    y += 80
    
    # 秘密揭示
    draw.rectangle([30, y, WIDTH-30, y+180], fill=hex_to_rgb('#F5EDE5'))
    y += 20
    draw.text((50, y), "古代御医的秘密", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 45
    draw.text((50, y), "乾隆皇帝80岁还能批阅奏章到深夜", font=font_text, fill=hex_to_rgb(COLORS['text_dark']))
    y += 35
    draw.text((50, y), "他的秘诀：每日一杯枸杞菊花茶", font=font_text, fill=hex_to_rgb(COLORS['text_gray']))
    y += 35
    draw.text((50, y), "现代科学验证：护眼效果提升3倍", font=font_text, fill=hex_to_rgb(COLORS['secondary']))
    y += 80
    
    # 理论解析
    draw.text((50, y), "中医理论", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 50
    theories = [
        "-> 眼睛是肝的窗户",
        "-> 肝血不足 = 眼睛干涩模糊",
        "-> 喝枸杞菊花茶 = 补肝养血"
    ]
    for t in theories:
        draw.text((50, y), t, font=font_text, fill=hex_to_rgb(COLORS['text_gray']))
        y += 38
    
    canvas.save(output_path, quality=100, dpi=(300, 300))
    print(f"2.经典: {os.path.getsize(output_path)//1024}KB")

def create_materials(image_path, output_path):
    """原料准备：图文混排"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(36, bold=True)
    font_name = load_font(28, bold=True)
    font_desc = load_font(22)
    
    # 顶部
    draw.rectangle([0, 0, WIDTH, 70], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, 20), "三种原料，缺一不可", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 材料卡片
    materials = [
        ("枸杞", "10g", "补肾生精，养肝明目", COLORS['primary']),
        ("菊花", "5朵", "清肝明目，清热解毒", COLORS['accent']),
        ("决明子", "5g", "清肝明目，润肠通便", COLORS['secondary']),
    ]
    
    y = 90
    for name, amount, desc, color in materials:
        # 卡片背景
        draw.rectangle([30, y, WIDTH-30, y+85], fill=hex_to_rgb(COLORS['bg_cream']))
        # 名称
        draw.text((50, y+15), name, font=font_name, fill=hex_to_rgb(color))
        draw.text((180, y+15), amount, font=font_name, fill=hex_to_rgb(COLORS['text_gray']))
        # 描述
        draw.text((50, y+52), desc, font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 100
    
    # 黄金搭配
    y += 15
    draw.text((50, y), "黄金搭配原理", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 45
    principles = ["枸杞补 - 滋养肝血", "菊花清 - 清除肝火", "决明子通 - 润肠通便"]
    for p in principles:
        draw.text((50, y), "* " + p, font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 35
    
    # 选品口诀
    y += 20
    draw.text((50, y), "选品口诀", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 45
    tips = ["枸杞：宁夏中宁，暗红饱满", "菊花：胎菊最好，花朵完整", "决明子：颗粒饱满无杂质"]
    for t in tips:
        draw.text((50, y), "- " + t, font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 35
    
    # 底部图片
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = fit_image_proportional(img, WIDTH-60, 280)
        canvas.paste(img, (30, HEIGHT-340))
    
    # 成本
    draw.rectangle([30, HEIGHT-50, WIDTH-30, HEIGHT-10], fill=hex_to_rgb('#FFF3E0'))
    draw.text((50, HEIGHT-40), "单杯成本：仅需 4.25元", font=font_desc, fill=hex_to_rgb(COLORS['primary']))
    
    canvas.save(output_path, quality=100, dpi=(300, 300))
    print(f"3.原料: {os.path.getsize(output_path)//1024}KB")

def create_method(image_path, output_path):
    """制作方法：左图右文"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    
    # 左侧图片
    if os.path.exists(image_path):
        img = Image.open(image_path)
        left_img = fit_image_proportional(img, int(WIDTH * 0.40), HEIGHT)
        canvas.paste(left_img, (0, 0))
    
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(34, bold=True)
    font_step = load_font(26)
    font_desc = load_font(20)
    
    x = int(WIDTH * 0.45)
    
    # 标题
    draw.text((x, 50), "5分钟搞定", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    
    # 步骤
    steps = [
        ("1", "材料清洗", "枸杞快速冲洗"),
        ("2", "放入杯中", "决明子先放"),
        ("3", "热水冲泡", "85度焖泡5分钟"),
    ]
    
    y = 120
    for num, title, desc in steps:
        # 编号圆圈
        draw.ellipse([x, y, x+38, y+38], fill=hex_to_rgb(COLORS['accent']))
        draw.text((x+11, y+5), num, font=load_font(22, bold=True), fill=hex_to_rgb(COLORS['text_light']))
        # 标题和描述
        draw.text((x+50, y+3), title, font=font_step, fill=hex_to_rgb(COLORS['text_dark']))
        draw.text((x+50, y+32), desc, font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 70
    
    # 进阶技巧
    y += 20
    draw.rectangle([x-10, y, WIDTH-20, y+110], fill=hex_to_rgb(COLORS['bg_cream']))
    draw.text((x+10, y+12), "进阶技巧", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 42
    tips = ["可加蜂蜜调味", "可续水2-3次", "枸杞直接吃掉"]
    for t in tips:
        draw.text((x+10, y), "- " + t, font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
        y += 25
    
    # 最佳时间
    y += 25
    draw.text((x, y), "最佳饮用时间", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 38
    draw.text((x, y), "下午3-5点", font=font_step, fill=hex_to_rgb(COLORS['accent']))
    y += 35
    draw.text((x, y), "膀胱经当令，排毒黄金时段", font=font_desc, fill=hex_to_rgb(COLORS['text_gray']))
    
    canvas.save(output_path, quality=100, dpi=(300, 300))
    print(f"4.方法: {os.path.getsize(output_path)//1024}KB")

def create_effect(image_path, output_path):
    """功效说明：全图背景"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_white']))
    
    # 背景图
    if os.path.exists(image_path):
        img = Image.open(image_path)
        bg = fit_image_proportional(img, WIDTH, HEIGHT)
        canvas.paste(bg, (0, 0))
        
        # 渐变遮罩
        for y in range(int(HEIGHT * 0.35), HEIGHT):
            alpha = int(230 * (y - HEIGHT * 0.35) / (HEIGHT * 0.65))
            for x in range(WIDTH):
                pixel = canvas.getpixel((x, y))
                new_color = tuple(int(pixel[i] * (255 - alpha) / 255 + 255 * alpha / 255) for i in range(3))
                canvas.putpixel((x, y), new_color)
    
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(40, bold=True)
    font_effect = load_font(28)
    font_data = load_font(22)
    
    y = int(HEIGHT * 0.40)
    draw.text((50, y), "坚持喝，你会看到变化", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 65
    
    effects = [
        ("清肝明目", "1周后眼睛不再干涩"),
        ("滋补肝肾", "2周后视力更清晰"),
        ("抗氧抗衰", "1月后眼袋淡化"),
    ]
    
    for title, desc in effects:
        draw.text((50, y), "V " + title, font=font_effect, fill=hex_to_rgb(COLORS['text_dark']))
        draw.text((85, y+35), desc, font=font_data, fill=hex_to_rgb(COLORS['text_gray']))
        y += 80
    
    y += 20
    draw.text((50, y), "效果时间线", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 48
    timeline = ["1周 -> 眼干缓解", "2周 -> 视力清晰", "1月 -> 黑眼圈淡化"]
    for t in timeline:
        draw.text((50, y), t, font=font_data, fill=hex_to_rgb(COLORS['text_gray']))
        y += 35
    
    canvas.save(output_path, quality=100, dpi=(300, 300))
    print(f"5.功效: {os.path.getsize(output_path)//1024}KB")

def create_tips(output_path):
    """温馨提示"""
    canvas = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(COLORS['bg_cream']))
    draw = ImageDraw.Draw(canvas)
    
    font_title = load_font(34, bold=True)
    font_text = load_font(24)
    font_small = load_font(20)
    
    # 顶部
    draw.rectangle([0, 0, WIDTH, 70], fill=hex_to_rgb(COLORS['primary']))
    draw.text((50, 20), "饮用指南", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    # 饮用建议
    y = 90
    draw.rectangle([25, y, WIDTH-25, y+130], fill=hex_to_rgb(COLORS['bg_white']))
    draw.text((45, y+12), "饮用建议", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 42
    tips = ["最佳时间：下午3-5点", "最佳频率：每天1杯", "最佳温度：温热饮用"]
    for t in tips:
        draw.text((45, y), "* " + t, font=font_text, fill=hex_to_rgb(COLORS['text_gray']))
        y += 28
    
    # 禁忌
    y = 250
    draw.rectangle([25, y, WIDTH-25, y+130], fill=hex_to_rgb('#FFEBEE'))
    draw.text((45, y+12), "禁忌人群", font=font_title, fill=hex_to_rgb('#C62828'))
    y += 42
    forbidden = ["孕妇慎用决明子", "脾胃虚寒者饭后饮用", "感冒发烧时暂停"]
    for f in forbidden:
        draw.text((45, y), "X " + f, font=font_text, fill=hex_to_rgb(COLORS['text_gray']))
        y += 28
    
    # Q&A
    y = 410
    draw.text((50, y), "常见问题", font=font_title, fill=hex_to_rgb(COLORS['secondary']))
    y += 42
    qa = ["Q: 喝了拉肚子？ A: 减量或饭后喝", "Q: 可以不加决明子？ A: 可以但效果打折"]
    for q in qa:
        draw.text((50, y), q, font=font_small, fill=hex_to_rgb(COLORS['text_gray']))
        y += 28
    
    # 互动
    y += 20
    draw.text((50, y), "互动引导", font=font_title, fill=hex_to_rgb(COLORS['primary']))
    y += 42
    interactions = ["点赞收藏，下次翻出来", "评论区晒你的变化", "关注解锁更多养生秘籍"]
    for i in interactions:
        draw.text((50, y), "-> " + i, font=font_text, fill=hex_to_rgb(COLORS['text_dark']))
        y += 32
    
    # 标签
    y += 15
    draw.text((50, y), "#赤兔养生 #职场养生 #护眼", font=font_small, fill=hex_to_rgb(COLORS['accent']))
    
    # 底部
    draw.rectangle([0, HEIGHT-65, WIDTH, HEIGHT], fill=hex_to_rgb(COLORS['secondary']))
    draw.text((50, HEIGHT-45), "赤兔养生计划", font=font_title, fill=hex_to_rgb(COLORS['text_light']))
    
    canvas.save(output_path, quality=100, dpi=(300, 300))
    print(f"6.提示: {os.path.getsize(output_path)//1024}KB")

def main():
    output_dir = os.path.expanduser("~/.openclaw/media/xhs-final/")
    os.makedirs(output_dir, exist_ok=True)
    
    goji = os.path.expanduser("~/.openclaw/media/素材_枸杞.jpg")
    chrys = os.path.expanduser("~/.openclaw/media/素材_菊花.jpg")
    tea = os.path.expanduser("~/.openclaw/media/素材_养生茶.jpg")
    
    print("生成广告级配图...\n")
    
    create_cover(tea, output_dir + "01_封面.png")
    create_classic(output_dir + "02_中医经典.png")
    create_materials(goji, output_dir + "03_原料准备.png")
    create_method(tea, output_dir + "04_制作方法.png")
    create_effect(chrys, output_dir + "05_功效说明.png")
    create_tips(output_dir + "06_温馨提示.png")
    
    print(f"\n完成！位置: {output_dir}")

if __name__ == "__main__":
    main()
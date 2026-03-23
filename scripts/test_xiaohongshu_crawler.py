#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书爬虫 - 测试验证脚本
赤兔计划 (RED-RABBIT) - 任务 ID: recvetJHM0itG2

用于验证爬虫脚本的安装和配置是否正确
"""

import sys
import json
from pathlib import Path
from datetime import datetime


def test_imports():
    """测试依赖导入"""
    print("=" * 60)
    print("📦 测试依赖导入")
    print("=" * 60)
    
    tests = [
        ("playwright", "浏览器自动化"),
        ("asyncio", "异步支持"),
    ]
    
    results = []
    for module, description in tests:
        try:
            __import__(module)
            print(f"✅ {description}: {module}")
            results.append(True)
        except ImportError as e:
            print(f"❌ {description}: {module} - {e}")
            results.append(False)
    
    return all(results)


def test_script_structure():
    """测试脚本结构"""
    print("\n" + "=" * 60)
    print("📁 测试脚本结构")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    required_files = [
        "xiaohongshu_crawler.py",
        "xiaohongshu_crawler_openclaw.py",
        "xiaohongshu_crawler_requirements.txt",
        "README_XIAOHONGSHU_CRAWLER.md",
    ]
    
    results = []
    for file in required_files:
        file_path = script_dir / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {file} ({size} 字节)")
            results.append(True)
        else:
            print(f"❌ {file} - 文件不存在")
            results.append(False)
    
    return all(results)


def test_config():
    """测试配置"""
    print("\n" + "=" * 60)
    print("⚙️  测试配置")
    print("=" * 60)
    
    # 导入配置
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from xiaohongshu_crawler import Config
        
        print(f"✅ 飞书 App Token: {Config.FEISHU_BITABLE_APP_TOKEN}")
        print(f"✅ 飞书 Table ID: {Config.FEISHU_BITABLE_TABLE_ID}")
        print(f"✅ 搜索关键词：{Config.KEYWORDS}")
        print(f"✅ 每关键词最大笔记数：{Config.MAX_NOTES_PER_KEYWORD}")
        
        return True
    except Exception as e:
        print(f"❌ 配置加载失败：{e}")
        return False


def test_data_model():
    """测试数据模型"""
    print("\n" + "=" * 60)
    print("📊 测试数据模型")
    print("=" * 60)
    
    try:
        from xiaohongshu_crawler import NoteData
        
        # 创建测试数据
        note = NoteData()
        note.note_id = "test_123"
        note.title = "测试笔记标题"
        note.author_name = "测试作者"
        note.like_count = 100
        note.collect_count = 50
        note.content = "这是测试内容"
        note.tags = ["#养生", "#健康"]
        note.search_keyword = "养生茶"
        
        # 转换为字典
        data_dict = note.to_dict()
        print(f"✅ 数据模型创建成功")
        print(f"   字段数：{len(data_dict)}")
        print(f"   示例字段：{list(data_dict.keys())[:5]}")
        
        # 转换为飞书字段
        feishu_fields = note.to_feishu_fields()
        print(f"✅ 飞书字段转换成功")
        print(f"   字段数：{len(feishu_fields)}")
        
        return True
    except Exception as e:
        print(f"❌ 数据模型测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_logger():
    """测试日志工具"""
    print("\n" + "=" * 60)
    print("📝 测试日志工具")
    print("=" * 60)
    
    try:
        from xiaohongshu_crawler import Logger
        from pathlib import Path
        
        log_file = Path(__file__).parent / "test_crawler.log"
        logger = Logger(log_file)
        
        logger.info("测试信息")
        logger.warning("测试警告")
        logger.error("测试错误")
        
        # 检查日志文件
        if log_file.exists():
            content = log_file.read_text(encoding="utf-8")
            print(f"✅ 日志文件创建成功：{log_file}")
            print(f"   日志行数：{len(content.splitlines())}")
            
            # 清理测试日志
            log_file.unlink()
            print(f"✅ 测试日志已清理")
            
            return True
        else:
            print(f"❌ 日志文件未创建")
            return False
    except Exception as e:
        print(f"❌ 日志工具测试失败：{e}")
        return False


def test_feishu_export():
    """测试飞书数据导出"""
    print("\n" + "=" * 60)
    print("💾 测试飞书数据导出")
    print("=" * 60)
    
    try:
        from xiaohongshu_crawler import NoteData, Config
        
        # 创建测试数据
        notes = []
        for i in range(3):
            note = NoteData()
            note.note_id = f"test_{i}"
            note.title = f"测试笔记 {i}"
            note.author_name = f"作者 {i}"
            note.like_count = 100 * (i + 1)
            note.collect_count = 50 * (i + 1)
            note.content = f"测试内容 {i}"
            note.tags = ["#测试", f"#标签{i}"]
            note.search_keyword = "养生茶"
            notes.append(note)
        
        # 导出为 JSON
        export_file = Path(__file__).parent / "test_export.json"
        records = [{"fields": note.to_feishu_fields()} for note in notes]
        
        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 测试数据导出成功：{export_file}")
        print(f"   记录数：{len(records)}")
        
        # 验证导出文件
        with open(export_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        
        print(f"✅ 导出文件验证成功")
        print(f"   第一条记录标题：{loaded[0]['fields']['标题']}")
        
        # 清理测试文件
        export_file.unlink()
        print(f"✅ 测试文件已清理")
        
        return True
    except Exception as e:
        print(f"❌ 飞书数据导出测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚀 小红书爬虫 - 测试验证")
    print("赤兔计划 (RED-RABBIT) - 任务 ID: recvetJHM0itG2")
    print("=" * 60)
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 运行所有测试
    tests = [
        ("依赖导入", test_imports),
        ("脚本结构", test_script_structure),
        ("配置检查", test_config),
        ("数据模型", test_data_model),
        ("日志工具", test_logger),
        ("飞书导出", test_feishu_export),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} 测试异常：{e}")
            results.append((name, False))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print()
    print(f"总计：{passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！爬虫已准备就绪。")
        print("\n下一步:")
        print("1. 运行：python xiaohongshu_crawler.py")
        print("2. 在浏览器中登录小红书账号")
        print("3. 等待抓取完成")
        print("4. 查看日志和数据文件")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查配置和依赖。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

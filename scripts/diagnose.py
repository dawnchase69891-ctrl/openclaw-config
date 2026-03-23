#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P2 模块诊断脚本

功能:
- 检查 Python 环境
- 检查依赖
- 检查文件结构
- 检查 OpenClaw 状态
- 运行快速测试

使用:
    python3 scripts/diagnose.py
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / '.openclaw' / 'workspace'


def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"Python 版本：{version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 11:
        print("✅ Python 版本符合要求 (>= 3.11)")
        return True
    else:
        print("❌ Python 版本过低，需要 >= 3.11")
        return False


def check_dependencies():
    """检查依赖"""
    deps = [
        ('pytest', 'pytest'),
        ('pytest_mock', 'pytest-mock'),
        ('pytest_asyncio', 'pytest-asyncio'),
    ]
    
    missing = []
    
    for module, package in deps:
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (缺失)")
            missing.append(package)
    
    if missing:
        print(f"\n安装命令：pip install {' '.join(missing)}")
        return False
    
    print("\n✅ 依赖检查通过")
    return True


def check_files():
    """检查文件结构"""
    required_files = [
        ('脚本', [
            'scripts/feishu_doc_creator.py',
            'scripts/collaboration_utils.py',
            'scripts/task_queue_manager.py',
        ]),
        ('模板', [
            'docs/templates/task-template.md',
            'docs/templates/decision-template.md',
            'docs/templates/meeting-template.md',
            'docs/templates/daily-report-template.md',
        ]),
        ('测试', [
            'tests/conftest.py',
            'tests/test_integration.py',
        ]),
        ('文档', [
            'docs/P2-API 文档.md',
            'docs/P2-部署指南.md',
            'docs/P2-故障排查指南.md',
        ]),
    ]
    
    all_exist = True
    
    for category, files in required_files:
        print(f"\n{category}:")
        missing = []
        
        for file_path in files:
            full_path = WORKSPACE / file_path
            if full_path.exists():
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path} (缺失)")
                missing.append(file_path)
                all_exist = False
    
    return all_exist


def check_openclaw():
    """检查 OpenClaw 状态"""
    print("\nOpenClaw 状态:")
    
    try:
        # 检查网关状态
        result = subprocess.run(
            ['openclaw', 'gateway', 'status'],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            print(f"  ✅ 网关：运行中")
            gateway_ok = True
        else:
            print(f"  ⚠️ 网关：未运行或状态异常")
            gateway_ok = False
            
    except FileNotFoundError:
        print(f"  ❌ openclaw 命令未找到")
        return False
    except Exception as e:
        print(f"  ❌ 检查失败：{e}")
        return False
    
    try:
        # 检查会话列表
        result = subprocess.run(
            ['openclaw', 'sessions', 'list'],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            sessions = result.stdout.strip().split('\n')
            print(f"  ✅ 会话：{len(sessions)} 个")
            sessions_ok = True
        else:
            print(f"  ⚠️ 会话：无法获取")
            sessions_ok = False
            
    except Exception as e:
        print(f"  ❌ 检查失败：{e}")
        return False
    
    return gateway_ok and sessions_ok


def run_quick_test():
    """运行快速测试"""
    print("\n快速测试:")
    
    # 测试文档创建器
    try:
        result = subprocess.run(
            ['python3', 'scripts/feishu_doc_creator.py', 'list-templates'],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            print("  ✅ 文档创建器：正常")
            doc_creator_ok = True
        else:
            print(f"  ❌ 文档创建器：失败")
            print(f"     错误：{result.stderr[:100]}")
            doc_creator_ok = False
            
    except Exception as e:
        print(f"  ❌ 文档创建器：异常 {e}")
        doc_creator_ok = False
    
    # 测试协作工具
    try:
        result = subprocess.run(
            ['python3', 'scripts/collaboration_utils.py'],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            print("  ✅ 协作工具：正常")
            collab_ok = True
        else:
            print(f"  ❌ 协作工具：失败")
            collab_ok = False
            
    except Exception as e:
        print(f"  ❌ 协作工具：异常 {e}")
        collab_ok = False
    
    # 测试任务队列
    try:
        result = subprocess.run(
            ['python3', 'scripts/task_queue_manager.py', 'status'],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=WORKSPACE
        )
        
        if result.returncode == 0:
            print("  ✅ 任务队列：正常")
            queue_ok = True
        else:
            print(f"  ❌ 任务队列：失败")
            queue_ok = False
            
    except Exception as e:
        print(f"  ❌ 任务队列：异常 {e}")
        queue_ok = False
    
    return doc_creator_ok and collab_ok and queue_ok


def check_directories():
    """检查必要目录"""
    print("\n必要目录:")
    
    dirs = [
        '.dead-letter',
        '.backup/config',
        'docs/templates',
        'tests',
    ]
    
    all_ok = True
    
    for dir_path in dirs:
        full_path = WORKSPACE / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ⚠️ {dir_path}/ (不存在，可自动创建)")
    
    return True  # 目录不存在不影响功能


def generate_report(checks):
    """生成诊断报告"""
    print("\n" + "=" * 70)
    print("诊断报告")
    print("=" * 70)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"时间：{timestamp}")
    print(f"工作空间：{WORKSPACE}")
    print()
    
    passed = sum(1 for _, r in checks if r)
    total = len(checks)
    
    for name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print()
    print(f"总计：{passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有检查通过！系统运行正常。")
        print("\n建议:")
        print("  - 运行集成测试：pytest tests/test_integration.py -v")
        print("  - 查看 API 文档：docs/P2-API 文档.md")
    else:
        print("\n⚠️ 部分检查失败，请查看上面的错误信息。")
        print("\n建议:")
        print("  - 根据错误信息修复问题")
        print("  - 查看部署指南：docs/P2-部署指南.md")
        print("  - 查看故障排查：docs/P2-故障排查指南.md")
    
    print("=" * 70)
    
    return passed == total


def main():
    """主诊断流程"""
    print("=" * 70)
    print("P2 模块诊断工具 v1.0")
    print("=" * 70)
    print()
    
    checks = [
        ("Python 环境", check_python_version),
        ("依赖检查", check_dependencies),
        ("文件结构", check_files),
        ("必要目录", check_directories),
        ("OpenClaw 状态", check_openclaw),
        ("快速测试", run_quick_test),
    ]
    
    results = []
    
    for name, check in checks:
        try:
            result = check()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} 检查异常：{e}")
            results.append((name, False))
    
    success = generate_report(results)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

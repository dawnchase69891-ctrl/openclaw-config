#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化调仓提醒系统
创建数据目录并迁移旧数据
"""

import os
import sys

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from feishu_rebalance_reminder import migrate_legacy_data

def main():
    print("🚀 初始化调仓提醒系统...")
    print()

    # 创建数据目录
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    print(f"✅ 数据目录已创建: {data_dir}")

    # 创建 lib 目录
    lib_dir = os.path.join(os.path.dirname(__file__), 'lib')
    os.makedirs(lib_dir, exist_ok=True)
    print(f"✅ Lib 目录已创建: {lib_dir}")

    # 迁移旧数据
    print()
    migrate_legacy_data()

    print()
    print("✅ 初始化完成！")
    print()
    print("📋 下一步操作:")
    print("  1. 设置 TUSHARE_TOKEN 环境变量")
    print("  2. 测试价格获取: python3 scripts/feishu_rebalance_reminder.py refresh")
    print("  3. 发送盘前提醒: python3 scripts/feishu_rebalance_reminder.py morning")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆迁移脚本
将现有 MEMORY.md 和 QIJI_GROWTH.md 中的关键信息迁移到 Mem0
同时保持原有文件不变 (作为备份和主存储)
"""

import re
from pathlib import Path
import subprocess
import json

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
MEMORY_FILE = WORKSPACE / 'MEMORY.md'
GROWTH_FILE = WORKSPACE / '.learnings' / 'QIJI_GROWTH.md'
MEM0_SCRIPTS = WORKSPACE / 'skills' / 'mem0' / 'scripts'

class MemoryMigrator:
    """记忆迁移器"""
    
    def __init__(self):
        self.migrated_count = 0
        self.skipped_count = 0
    
    def extract_from_memory_md(self):
        """从 MEMORY.md 提取关键信息"""
        print("="*60)
        print("📋 从 MEMORY.md 提取信息")
        print("="*60)
        
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取用户偏好
        preferences = []
        if '## User Preferences' in content:
            # 提取文件安全规则
            if 'File Safety' in content:
                preferences.append("Jason 要求：删除文件前必须征得同意，修改文件前要备份")
            
            # 提取其他偏好
            if 'timezone' in content:
                preferences.append("Jason 的时区：Asia/Shanghai")
            
            if 'partners' in content:
                preferences.append("Jason 视骐骥为生活和工作的伙伴，不仅是工具")
        
        # 提取项目信息
        projects = []
        if '金融 Agent' in content:
            projects.append("当前重点：金融 Agent (Marcus) + 产研体系")
            projects.append("持仓股票：恒逸石化、汉缆股份、中矿资源、广电电气、中国卫通")
        
        if 'Content Factory' in content:
            projects.append("Content Factory 内容工厂：6 Agent 流水线")
        
        # 提取重要日期
        milestones = []
        if '2026-02-25' in content:
            milestones.append("2026-02-25: Jason 命名骐骥 (Qíjì) 🐎 - 千里马")
        
        return {
            'preferences': preferences,
            'projects': projects,
            'milestones': milestones
        }
    
    def extract_from_growth_md(self):
        """从 QIJI_GROWTH.md 提取学习"""
        print("\n" + "="*60)
        print("📝 从 QIJI_GROWTH.md 提取学习")
        print("="*60)
        
        with open(GROWTH_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        learnings = []
        
        # 提取成长原则
        if '每日复盘' in content:
            learnings.append("骐骥成长原则：每日复盘、主动学习、持续进化、知识沉淀")
        
        # 提取重要学习
        if '持仓配置同步' in content:
            learnings.append("经验教训：多文件配置容易遗漏，需要单一数据源")
        
        if 'web 驾驶舱' in content:
            learnings.append("系统要求：web 驾驶舱是实时监控中心，所有调整自动同步")
        
        if 'Marcus 人设' in content:
            learnings.append("Marcus 人设：15 年华尔街经验的日内交易策略师")
        
        return {'learnings': learnings}
    
    def add_to_mem0(self, text, category="general"):
        """添加到 Mem0"""
        try:
            # 使用本地存储模式，不需要 API key
            cmd = [
                'node', str(MEM0_SCRIPTS / 'mem0-add.js'),
                '--user=Jason',
                f'[{category}] {text}'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"  ✅ Mem0: {text[:50]}...")
                self.migrated_count += 1
                return True
            else:
                # 检查是否是 API key 问题
                if '401' in result.stderr or 'API key' in result.stderr:
                    print(f"  ⚠️ Mem0 需要 OpenAI API key，跳过此项")
                    print(f"     提示：设置 OPENAI_API_KEY 环境变量")
                    self.skipped_count += 1
                    return False
                else:
                    print(f"  ⚠️ 添加失败：{result.stderr[:100]}")
                    self.skipped_count += 1
                    return False
        except Exception as e:
            print(f"  ⚠️ 错误：{e}")
            self.skipped_count += 1
            return False
    
    def migrate(self):
        """执行迁移"""
        print("\n" + "="*60)
        print("🚀 开始记忆迁移")
        print("="*60)
        
        # 从 MEMORY.md 提取
        memory_data = self.extract_from_memory_md()
        
        # 从 QIJI_GROWTH.md 提取
        growth_data = self.extract_from_growth_md()
        
        # 添加到 Mem0
        print("\n" + "="*60)
        print("📤 添加到 Mem0")
        print("="*60)
        
        print("\n【用户偏好】")
        for pref in memory_data['preferences']:
            self.add_to_mem0(pref, 'preference')
        
        print("\n【项目信息】")
        for proj in memory_data['projects']:
            self.add_to_mem0(proj, 'project')
        
        print("\n【里程碑】")
        for ms in memory_data['milestones']:
            self.add_to_mem0(ms, 'milestone')
        
        print("\n【学习经验】")
        for lrn in growth_data['learnings']:
            self.add_to_mem0(lrn, 'learning')
        
        # 总结
        print("\n" + "="*60)
        print("📊 迁移完成")
        print("="*60)
        print(f"✅ 成功迁移：{self.migrated_count} 条")
        print(f"⚠️ 跳过：{self.skipped_count} 条")
        
        if self.skipped_count > 0:
            print("\n💡 提示:")
            print("   Mem0 需要 OpenAI API key 才能工作")
            print("   设置方法：export OPENAI_API_KEY=your_key")
            print("\n   现有记忆文件保持不变:")
            print(f"   - MEMORY.md: {MEMORY_FILE}")
            print(f"   - QIJI_GROWTH.md: {GROWTH_FILE}")
            print("   - memory/: ~/.openclaw/workspace/memory/")
    
    def create_backup_plan(self):
        """创建备份计划"""
        print("\n" + "="*60)
        print("💾 备份策略")
        print("="*60)
        
        backup_plan = """
# 记忆备份策略

## 现有系统 (保持不变)
- MEMORY.md: 长期事实记忆
- memory/YYYY-MM-DD.md: 每日记忆
- .learnings/QIJI_GROWTH.md: 成长日志

## Mem0 (补充层)
- 用户偏好
- 行为模式
- 对话上下文

## 备份规则
1. 所有原始文件保持不变
2. Mem0 作为快速检索层
3. 每周同步：Mem0 → MEMORY.md (提炼)
4. 每月备份：导出 Mem0 到 JSON

## 恢复流程
如果 Mem0 数据丢失:
1. 从 MEMORY.md 恢复事实
2. 从 QIJI_GROWTH.md 恢复学习
3. 重新添加偏好到 Mem0
"""
        print(backup_plan)
        
        # 保存备份计划
        backup_file = WORKSPACE / 'MEMORY_BACKUP.md'
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write("# 记忆备份策略\n\n" + backup_plan)
        print(f"✅ 备份计划已保存：{backup_file}")


def main():
    """主函数"""
    migrator = MemoryMigrator()
    
    print("="*60)
    print("🧠 骐骥记忆迁移工具")
    print("="*60)
    print("\n此工具将:")
    print("1. 从 MEMORY.md 和 QIJI_GROWTH.md 提取关键信息")
    print("2. 添加到 Mem0 作为快速检索层")
    print("3. 保持原有文件不变 (作为主存储)")
    print("4. 创建备份策略文档")
    
    confirm = input("\n是否继续？(y/n): ")
    if confirm.lower() != 'y':
        print("❌ 已取消")
        return
    
    # 执行迁移
    migrator.migrate()
    
    # 创建备份计划
    migrator.create_backup_plan()
    
    print("\n" + "="*60)
    print("✅ 迁移完成！")
    print("="*60)


if __name__ == '__main__':
    main()

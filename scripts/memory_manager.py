#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
骐骥记忆管理器
统一管理 MEMORY.md、daily memory、Mem0 和成长日志
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
MEMORY_FILE = WORKSPACE / 'MEMORY.md'
MEMORY_DIR = WORKSPACE / 'memory'
GROWTH_FILE = WORKSPACE / '.learnings' / 'QIJI_GROWTH.md'
MEM0_SCRIPTS = WORKSPACE / 'skills' / 'mem0' / 'scripts'

class MemoryManager:
    """记忆管理器"""
    
    def __init__(self):
        self.today = datetime.now()
        self.today_str = self.today.strftime('%Y-%m-%d')
        self.daily_file = MEMORY_DIR / f'{self.today_str}.md'
    
    def ensure_memory_dir(self):
        """确保 memory 目录存在"""
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_daily_memory(self):
        """获取今日记忆文件"""
        self.ensure_memory_dir()
        if not self.daily_file.exists():
            # 创建新的每日记忆
            content = f"""# {self.today_str}

## 任务
- [ ] 

## 对话要点
- 

## 决策
- 

## 学习
- 

## 待办
- 

---
*创建时间：{datetime.now().strftime('%H:%M')}*
"""
            with open(self.daily_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 创建今日记忆文件：{self.daily_file}")
        return self.daily_file
    
    def add_to_daily(self, section, content):
        """添加到每日记忆"""
        self.get_daily_memory()
        
        with open(self.daily_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 找到对应 section
        new_lines = []
        found_section = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if line.strip() == f'## {section}':
                found_section = True
                # 在下一行插入内容
                new_lines.append(f'- {content}\n')
        
        if not found_section:
            # 添加新 section
            new_lines.append(f'\n## {section}\n')
            new_lines.append(f'- {content}\n')
        
        with open(self.daily_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"✅ 已添加到每日记忆 [{section}]: {content}")
    
    def mem0_add(self, text):
        """添加到 Mem0"""
        try:
            cmd = ['node', str(MEM0_SCRIPTS / 'mem0-add.js'), text]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ 已添加到 Mem0: {text}")
            else:
                print(f"⚠️ Mem0 添加失败：{result.stderr}")
        except Exception as e:
            print(f"⚠️ Mem0 添加错误：{e}")
    
    def mem0_search(self, query, limit=3):
        """搜索 Mem0"""
        try:
            cmd = ['node', str(MEM0_SCRIPTS / 'mem0-search.js'), query, f'--limit={limit}']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"🔍 Mem0 搜索结果 [{query}]:")
                print(result.stdout)
                return result.stdout
            else:
                print(f"⚠️ Mem0 搜索失败：{result.stderr}")
        except Exception as e:
            print(f"⚠️ Mem0 搜索错误：{e}")
        return None
    
    def weekly_review(self):
        """每周回顾 - 提炼 daily memory 到 MEMORY.md"""
        print("="*60)
        print("📊 每周回顾")
        print("="*60)
        
        # 获取过去 7 天的 daily memories
        seven_days_ago = self.today - timedelta(days=7)
        memories = []
        
        for i in range(7):
            date = seven_days_ago + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            daily_file = MEMORY_DIR / f'{date_str}.md'
            
            if daily_file.exists():
                with open(daily_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    memories.append((date_str, content))
        
        print(f"找到 {len(memories)} 天的记忆")
        
        # 提炼重要内容
        important_items = []
        for date_str, content in memories:
            # 简单提取决策和学习
            if '## 决策' in content:
                important_items.append(f"### {date_str} 决策")
            if '## 学习' in content:
                important_items.append(f"### {date_str} 学习")
        
        if important_items:
            print("\n📝 建议提炼到 MEMORY.md:")
            for item in important_items:
                print(f"  - {item}")
        else:
            print("\n✅ 无需提炼内容")
    
    def cleanup_old_memories(self, days=30):
        """清理旧记忆"""
        print(f"🧹 清理 {days} 天前的记忆...")
        
        cutoff_date = self.today - timedelta(days=days)
        deleted = 0
        
        for file in MEMORY_DIR.glob('*.md'):
            try:
                # 从文件名解析日期
                date_str = file.stem
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if file_date < cutoff_date:
                    # 可以选择删除或归档
                    print(f"  🗑️  {file.name} (可归档)")
                    deleted += 1
            except:
                pass
        
        print(f"✅ 找到 {deleted} 个可归档的旧记忆")
    
    def generate_memory_report(self):
        """生成记忆报告"""
        print("="*60)
        print("📊 骐骥记忆报告")
        print("="*60)
        
        # 统计
        daily_count = len(list(MEMORY_DIR.glob('*.md')))
        growth_exists = GROWTH_FILE.exists()
        
        print(f"\n📋 核心记忆层:")
        print(f"  - 每日记忆：{daily_count} 天")
        print(f"  - 成长日志：{'✅' if growth_exists else '❌'}")
        
        # Mem0 统计
        print(f"\n🤖 动态记忆层 (Mem0):")
        try:
            cmd = ['node', str(MEM0_SCRIPTS / 'mem0-list.js')]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                print(f"  - Mem0 记忆：{len(lines)} 条")
        except:
            print(f"  - Mem0 记忆：统计失败")
        
        print(f"\n📊 领域记忆层:")
        domain_dirs = ['financial', 'product', 'system', 'skills']
        for domain in domain_dirs:
            domain_path = MEMORY_DIR / domain
            if domain_path.exists():
                count = len(list(domain_path.glob('*')))
                print(f"  - {domain}: {count} 文件")
            else:
                print(f"  - {domain}: 未创建")
        
        print(f"\n🔧 工具记忆层:")
        tool_files = ['TOOLS.md', 'AGENTS.md', 'SOUL.md']
        for tool in tool_files:
            tool_path = WORKSPACE / tool
            print(f"  - {tool}: {'✅' if tool_path.exists() else '❌'}")
        
        print("\n" + "="*60)


def main():
    """主函数"""
    import sys
    
    manager = MemoryManager()
    
    if len(sys.argv) < 2:
        print("用法：python3 memory_manager.py <command> [args]")
        print("\n命令:")
        print("  daily              - 获取/创建今日记忆")
        print("  add <section> <text> - 添加到每日记忆")
        print("  mem0-add <text>    - 添加到 Mem0")
        print("  mem0-search <text> - 搜索 Mem0")
        print("  weekly-review      - 每周回顾")
        print("  cleanup [days]     - 清理旧记忆")
        print("  report             - 生成记忆报告")
        return
    
    command = sys.argv[1]
    
    if command == 'daily':
        manager.get_daily_memory()
    
    elif command == 'add':
        if len(sys.argv) < 4:
            print("用法：python3 memory_manager.py add <section> <text>")
            return
        section = sys.argv[2]
        text = ' '.join(sys.argv[3:])
        manager.add_to_daily(section, text)
    
    elif command == 'mem0-add':
        if len(sys.argv) < 3:
            print("用法：python3 memory_manager.py mem0-add <text>")
            return
        text = ' '.join(sys.argv[2:])
        manager.mem0_add(text)
    
    elif command == 'mem0-search':
        if len(sys.argv) < 3:
            print("用法：python3 memory_manager.py mem0-search <text> [limit]")
            return
        text = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        manager.mem0_search(text, limit)
    
    elif command == 'weekly-review':
        manager.weekly_review()
    
    elif command == 'cleanup':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        manager.cleanup_old_memories(days)
    
    elif command == 'report':
        manager.generate_memory_report()
    
    else:
        print(f"未知命令：{command}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品调研助手
帮助 Product Agent 自动化执行市场调研任务
"""

import os
import json
from datetime import datetime

WORKSPACE = os.path.expanduser('~/.openclaw/workspace')
TEMPLATES_DIR = os.path.join(WORKSPACE, 'templates')
RESEARCH_DIR = os.path.join(WORKSPACE, 'research')

class ProductResearchAssistant:
    """产品调研助手"""
    
    def __init__(self):
        os.makedirs(RESEARCH_DIR, exist_ok=True)
    
    def create_research_project(self, name: str, description: str = '') -> dict:
        """创建调研项目"""
        project_dir = os.path.join(RESEARCH_DIR, name)
        os.makedirs(project_dir, exist_ok=True)
        
        # 创建项目结构
        files = {
            'market_research.md': self._load_template('market_research.md'),
            'competitor_analysis.md': self._load_template('competitor_analysis.md'),
            'user_research.md': self._load_template('user_research.md'),
            'product_roadmap.md': self._load_template('product_roadmap.md'),
            'notes.md': f'# 调研笔记\n\n项目：{name}\n创建日期：{datetime.now().strftime("%Y-%m-%d")}\n\n'
        }
        
        for filename, content in files.items():
            filepath = os.path.join(project_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        # 创建项目配置
        config = {
            'name': name,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'status': 'initiated',
            'tasks': []
        }
        
        with open(os.path.join(project_dir, 'config.json'), 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return {
            'success': True,
            'message': f'调研项目 {name} 已创建',
            'path': project_dir
        }
    
    def add_research_task(self, project: str, task: str, priority: str = 'P1') -> dict:
        """添加调研任务"""
        config_file = os.path.join(RESEARCH_DIR, project, 'config.json')
        
        if not os.path.exists(config_file):
            return {'success': False, 'message': '项目不存在'}
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        task_id = f"RT-{len(config.get('tasks', [])) + 1:03d}"
        config['tasks'].append({
            'id': task_id,
            'task': task,
            'priority': priority,
            'status': 'todo',
            'created_at': datetime.now().isoformat()
        })
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return {
            'success': True,
            'message': f'任务 {task_id} 已添加',
            'id': task_id
        }
    
    def generate_research_report(self, project: str) -> str:
        """生成调研报告摘要"""
        config_file = os.path.join(RESEARCH_DIR, project, 'config.json')
        
        if not os.path.exists(config_file):
            return '项目不存在'
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 统计任务
        tasks = config.get('tasks', [])
        total = len(tasks)
        done = sum(1 for t in tasks if t.get('status') == 'done')
        
        report = []
        report.append("=" * 80)
        report.append(f"📊 产品调研报告摘要 - {config['name']}")
        report.append("=" * 80)
        report.append(f"\n项目状态：{config.get('status', 'unknown')}")
        report.append(f"创建日期：{config.get('created_at', 'unknown')[:10]}")
        report.append(f"\n任务进度：{done}/{total} ({round(done/total*100) if total > 0 else 0}%)")
        
        report.append("\n任务列表:")
        for task in tasks:
            icon = "✅" if task.get('status') == 'done' else "⏳"
            priority = task.get('priority', 'P2')
            report.append(f"  {icon} [{priority}] {task['task']}")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def list_research_projects(self) -> list:
        """列出所有调研项目"""
        if not os.path.exists(RESEARCH_DIR):
            return []
        
        projects = []
        for name in os.listdir(RESEARCH_DIR):
            project_path = os.path.join(RESEARCH_DIR, name)
            if os.path.isdir(project_path):
                config_file = os.path.join(project_path, 'config.json')
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    projects.append({
                        'name': name,
                        'status': config.get('status', 'unknown'),
                        'tasks': len(config.get('tasks', [])),
                        'created': config.get('created_at', '')[:10]
                    })
        
        return projects
    
    def _load_template(self, filename: str) -> str:
        """加载模板文件"""
        template_path = os.path.join(TEMPLATES_DIR, filename)
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return f'# {filename.replace(".md", "").replace("_", " ").title()}\n\n'


def main():
    """命令行入口"""
    import sys
    
    assistant = ProductResearchAssistant()
    
    if len(sys.argv) < 2:
        print("用法：python3 product_research.py <command> [args]")
        print("\n可用命令:")
        print("  create <name> [description]  创建调研项目")
        print("  add-task <project> <task>    添加调研任务")
        print("  report <project>             生成调研报告")
        print("  list                         列出所有项目")
        return
    
    command = sys.argv[1]
    
    if command == 'create':
        name = sys.argv[2] if len(sys.argv) > 2 else 'unnamed'
        description = sys.argv[3] if len(sys.argv) > 3 else ''
        result = assistant.create_research_project(name, description)
        print(f"✅ {result['message']}")
        print(f"📁 项目路径：{result['path']}")
    
    elif command == 'add-task':
        if len(sys.argv) < 4:
            print("用法：add-task <project> <task>")
            return
        result = assistant.add_research_task(sys.argv[2], sys.argv[3])
        print(f"✅ {result['message']}")
    
    elif command == 'report':
        if len(sys.argv) < 3:
            print("用法：report <project>")
            return
        report = assistant.generate_research_report(sys.argv[2])
        print(report)
    
    elif command == 'list':
        projects = assistant.list_research_projects()
        if projects:
            print("📋 调研项目列表:")
            for proj in projects:
                print(f"  • {proj['name']} ({proj['status']}) - {proj['tasks']} 个任务 - 创建于 {proj['created']}")
        else:
            print("暂无调研项目")
    
    else:
        print(f"❌ 未知命令：{command}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产研团队项目管理器
实现项目流程的自动化管理
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class ProjectManager:
    """项目管理器"""
    
    def __init__(self):
        self.workspace = os.path.expanduser('~/.openclaw/workspace')
        self.projects_dir = os.path.join(self.workspace, 'projects')
        self.requirements_file = os.path.join(self.workspace, 'requirements.json')
        self.tasks_file = os.path.join(self.workspace, 'TASKS.json')
        self.metrics_file = os.path.join(self.workspace, 'METRICS.json')
        
        # 确保目录存在
        os.makedirs(self.projects_dir, exist_ok=True)
        
    # ========== 项目管理 ==========
    
    def create_project(self, name: str, charter: Dict) -> Dict:
        """创建项目"""
        project_dir = os.path.join(self.projects_dir, name)
        os.makedirs(project_dir, exist_ok=True)
        
        # 创建项目章程
        charter['name'] = name
        charter['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        charter['status'] = 'initiated'
        
        charter_file = os.path.join(project_dir, 'PROJECT_CHARTER.md')
        with open(charter_file, 'w', encoding='utf-8') as f:
            f.write(self._format_charter(charter))
        
        # 创建项目结构
        self._create_project_structure(project_dir)
        
        # 记录指标
        self._log_metric('project_created', {'name': name})
        
        return {
            'success': True,
            'message': f'项目 {name} 已创建',
            'path': project_dir
        }
    
    def _create_project_structure(self, project_dir: str):
        """创建项目目录结构"""
        dirs = ['docs', 'src', 'tests', 'releases']
        for d in dirs:
            os.makedirs(os.path.join(project_dir, d), exist_ok=True)
        
        # 创建空文件
        files = {
            'README.md': f'# 项目文档\n\n创建日期：{datetime.now().strftime("%Y-%m-%d")}\n',
            'TASKS.md': '# 任务列表\n\n## 待办\n\n',
            'TEST_PLAN.md': '# 测试计划\n\n',
            'RELEASE_NOTES.md': '# 发布说明\n\n',
            'RETROSPECTIVE.md': '# 项目回顾\n\n'
        }
        
        for filename, content in files.items():
            filepath = os.path.join(project_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    def _format_charter(self, charter: Dict) -> str:
        """格式化项目章程"""
        return f"""# 项目章程 - {charter.get('name', '未命名')}

**创建日期**: {charter.get('created_at', '未知')}
**状态**: {charter.get('status', 'initiated')}

## 项目背景
{charter.get('background', '暂无描述')}

## 项目目标
{self._format_list(charter.get('goals', []))}

## 成功标准
{charter.get('success_criteria', '暂无')}

## 资源需求
- 人力：{', '.join(charter.get('team', []))}
- 时间：{charter.get('timeline', '未定')}

## 风险评估
{charter.get('risks', '暂无')}

---
*本文档由 Project Manager 自动生成*
"""
    
    # ========== 需求管理 ==========
    
    def add_requirement(self, req: Dict) -> Dict:
        """添加需求"""
        requirements = self._load_requirements()
        
        # 生成 ID
        req_id = f"REQ-{len(requirements.get('backlog', [])) + 1:03d}"
        req['id'] = req_id
        req['status'] = 'backlog'
        req['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        if 'backlog' not in requirements:
            requirements['backlog'] = []
        
        requirements['backlog'].append(req)
        self._save_requirements(requirements)
        
        self._log_metric('requirement_added', {'id': req_id, 'title': req.get('title', '')})
        
        return {
            'success': True,
            'message': f'需求 {req_id} 已添加',
            'id': req_id
        }
    
    def analyze_requirement(self, req_id: str) -> Dict:
        """分析需求"""
        requirements = self._load_requirements()
        
        # 查找需求
        req = None
        for r in requirements.get('backlog', []):
            if r['id'] == req_id:
                req = r
                break
        
        if not req:
            return {'success': False, 'message': f'需求不存在：{req_id}'}
        
        # 生成分析
        analysis = {
            'user_stories': self._generate_user_stories(req),
            'acceptance_criteria': self._generate_acceptance_criteria(req),
            'priority': req.get('priority', 'P2'),
            'effort_estimate': self._estimate_effort(req),
            'risks': self._identify_risks(req)
        }
        
        req['status'] = 'analyzed'
        req['analysis'] = analysis
        req['analyzed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        self._save_requirements(requirements)
        
        return {
            'success': True,
            'message': f'需求 {req_id} 已分析',
            'analysis': analysis
        }
    
    # ========== 任务管理 ==========
    
    def create_task(self, project: str, task: Dict) -> Dict:
        """创建任务"""
        tasks_file = os.path.join(self.projects_dir, project, 'TASKS.md')
        
        task_id = f"TASK-{self._count_tasks(project) + 1:03d}"
        task['id'] = task_id
        task['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        task['status'] = 'todo'
        
        content = f"\n### {task_id}: {task.get('title', '未命名')}\n"
        content += f"- **负责人**: {task.get('assignee', '未分配')}\n"
        content += f"- **估算工时**: {task.get('estimate', '未知')}小时\n"
        content += f"- **状态**: {task['status']}\n"
        content += f"- **创建时间**: {task['created_at']}\n"
        
        with open(tasks_file, 'a', encoding='utf-8') as f:
            f.write(content)
        
        self._log_metric('task_created', {'project': project, 'id': task_id})
        
        return {
            'success': True,
            'message': f'任务 {task_id} 已创建',
            'id': task_id
        }
    
    def update_task_status(self, project: str, task_id: str, status: str, assignee: str) -> Dict:
        """更新任务状态"""
        tasks_file = os.path.join(self.projects_dir, project, 'TASKS.md')
        
        if not os.path.exists(tasks_file):
            return {'success': False, 'message': '任务文件不存在'}
        
        with open(tasks_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新状态
        old_status_line = f"- **状态**: todo\n"
        new_status_line = f"- **状态**: {status}\n"
        content = content.replace(old_status_line, new_status_line)
        
        # 更新负责人
        if assignee:
            old_assignee_line = "- **负责人**: 未分配\n"
            new_assignee_line = f"- **负责人**: {assignee}\n"
            content = content.replace(old_assignee_line, new_assignee_line)
        
        with open(tasks_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self._log_metric('task_updated', {'project': project, 'id': task_id, 'status': status})
        
        return {
            'success': True,
            'message': f'任务 {task_id} 状态已更新为 {status}'
        }
    
    # ========== 质量管理 ==========
    
    def get_metrics(self) -> Dict:
        """获取项目指标"""
        if not os.path.exists(self.metrics_file):
            return {'projects': 0, 'requirements': 0, 'tasks': 0}
        
        with open(self.metrics_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _log_metric(self, event_type: str, data: Dict):
        """记录指标"""
        metrics = self.get_metrics()
        
        if 'events' not in metrics:
            metrics['events'] = []
        
        metrics['events'].append({
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        
        # 更新计数
        if event_type == 'project_created':
            metrics['projects'] = metrics.get('projects', 0) + 1
        elif event_type == 'requirement_added':
            metrics['requirements'] = metrics.get('requirements', 0) + 1
        elif event_type == 'task_created':
            metrics['tasks'] = metrics.get('tasks', 0) + 1
        
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
    
    # ========== 辅助方法 ==========
    
    def _load_requirements(self) -> Dict:
        """加载需求"""
        if os.path.exists(self.requirements_file):
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'backlog': [], 'analyzed': [], 'approved': [], 'in_development': [], 'done': []}
    
    def _save_requirements(self, requirements: Dict):
        """保存需求"""
        with open(self.requirements_file, 'w', encoding='utf-8') as f:
            json.dump(requirements, f, ensure_ascii=False, indent=2)
    
    def _count_tasks(self, project: str) -> int:
        """计算任务数量"""
        tasks_file = os.path.join(self.projects_dir, project, 'TASKS.md')
        if not os.path.exists(tasks_file):
            return 0
        
        with open(tasks_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content.count('### TASK-')
    
    def _format_list(self, items: List[str]) -> str:
        """格式化列表"""
        if not items:
            return '暂无'
        return '\n'.join(f'- {item}' for item in items)
    
    def _generate_user_stories(self, req: Dict) -> List[str]:
        """生成用户故事"""
        return [
            f"作为用户，我希望{req.get('description', '实现功能')}",
            f"以便{req.get('benefit', '获得价值')}"
        ]
    
    def _generate_acceptance_criteria(self, req: Dict) -> List[str]:
        """生成验收标准"""
        return [
            "功能正常工作",
            "无严重 Bug",
            "性能符合要求"
        ]
    
    def _estimate_effort(self, req: Dict) -> str:
        """估算工作量"""
        priority = req.get('priority', 'P2')
        estimates = {'P0': '1-2 天', 'P1': '3-5 天', 'P2': '1 周', 'P3': '2 周'}
        return estimates.get(priority, '未知')
    
    def _identify_risks(self, req: Dict) -> List[str]:
        """识别风险"""
        return ["技术风险", "时间风险"]


def main():
    """命令行入口"""
    import sys
    
    pm = ProjectManager()
    
    if len(sys.argv) < 2:
        print("用法：python3 project_manager.py <command> [args]")
        print("\n可用命令:")
        print("  create-project <name>           创建项目")
        print("  add-requirement <title>         添加需求")
        print("  create-task <project> <title>   创建任务")
        print("  metrics                         查看指标")
        return
    
    command = sys.argv[1]
    
    if command == 'create-project':
        name = sys.argv[2] if len(sys.argv) > 2 else 'unnamed'
        result = pm.create_project(name, {
            'background': '待补充',
            'goals': ['目标 1', '目标 2'],
            'team': ['Product Agent', 'Development Agent'],
            'timeline': '2 周'
        })
        print(f"✅ {result['message']}")
        print(f"📁 项目路径：{result['path']}")
    
    elif command == 'metrics':
        metrics = pm.get_metrics()
        print("📊 项目指标")
        print(f"  项目数：{metrics.get('projects', 0)}")
        print(f"  需求数：{metrics.get('requirements', 0)}")
        print(f"  任务数：{metrics.get('tasks', 0)}")
    
    else:
        print(f"❌ 未知命令：{command}")


if __name__ == '__main__':
    main()

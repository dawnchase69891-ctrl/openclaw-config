#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务调度中心
Coordinator Agent 用来分配任务给各 Agent
"""

import os
import json
from datetime import datetime

WORKSPACE = os.path.expanduser('~/.openclaw/workspace')
TASKS_FILE = os.path.join(WORKSPACE, 'TASKS.json')
AGENTS_FILE = os.path.join(WORKSPACE, 'AGENTS_STATUS.json')

class TaskDispatcher:
    """任务调度中心"""
    
    def __init__(self):
        self.agents = {
            'Product Agent': {'file': 'product_agent.py', 'status': 'available'},
            'UI/UX Designer': {'file': 'ui_designer_agent.py', 'status': 'available'},
            'Development Agent': {'file': 'development_workspace.py', 'status': 'available'},
            'Code Review Agent': {'file': 'code_review_agent.py', 'status': 'available'},
            'QA Agent': {'file': 'test_qa_agent.py', 'status': 'available'},
            'DevOps Agent': {'file': 'devops_agent.py', 'status': 'available'},
            'Monitoring Agent': {'file': 'monitoring_agent.py', 'status': 'available'},
            'Documentation Agent': {'file': 'documentation_agent.py', 'status': 'available'}
        }
        self._load_agents_status()
    
    def _load_agents_status(self):
        """加载 Agent 状态"""
        if os.path.exists(AGENTS_FILE):
            with open(AGENTS_FILE, 'r', encoding='utf-8') as f:
                saved_status = json.load(f)
                for name, status in saved_status.items():
                    if name in self.agents:
                        self.agents[name].update(status)
    
    def _save_agents_status(self):
        """保存 Agent 状态"""
        with open(AGENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.agents, f, ensure_ascii=False, indent=2)
    
    def assign_task(self, agent_name: str, task: str, priority: str = 'P1', 
                    deadline: str = None, description: str = '') -> dict:
        """分配任务给 Agent"""
        
        if agent_name not in self.agents:
            return {'success': False, 'message': f'Agent 不存在：{agent_name}'}
        
        # 生成任务 ID
        task_id = f"TASK-{datetime.now().strftime('%Y%m%d')}-{self._count_tasks() + 1:03d}"
        
        # 创建任务
        task_data = {
            'id': task_id,
            'agent': agent_name,
            'task': task,
            'description': description,
            'priority': priority,
            'deadline': deadline,
            'status': 'assigned',
            'assigned_at': datetime.now().isoformat(),
            'completed_at': None,
            'result': None
        }
        
        # 保存任务
        tasks = self._load_tasks()
        tasks.append(task_data)
        self._save_tasks(tasks)
        
        # 更新 Agent 状态
        self.agents[agent_name]['status'] = 'busy'
        self.agents[agent_name]['current_task'] = task_id
        self._save_agents_status()
        
        # 生成调度通知
        notification = self._generate_notification(task_data)
        
        return {
            'success': True,
            'message': f'任务已分配给 {agent_name}',
            'task_id': task_id,
            'notification': notification
        }
    
    def _generate_notification(self, task_data: dict) -> str:
        """生成任务分配通知"""
        agent = task_data['agent']
        task = task_data['task']
        priority = task_data['priority']
        deadline = task_data['deadline'] or '待定'
        
        priority_icon = {'P0': '🔴', 'P1': '🟡', 'P2': '🔵', 'P3': '⚪'}
        
        return f"""
╔═══════════════════════════════════════════════════════════╗
║  📋 新任务分配                                            ║
╠═══════════════════════════════════════════════════════════╣
║  接收人：{agent:<20}                           ║
║  优先级：{priority_icon.get(priority, '⚪')} {priority:<20}                      ║
║  截止：{deadline:<20}                      ║
╠═══════════════════════════════════════════════════════════╣
║  任务内容：                                               ║
║  {task:<54} ║
╠═══════════════════════════════════════════════════════════╣
║  任务 ID: {task_data['id']:<46} ║
╚═══════════════════════════════════════════════════════════╝
"""
    
    def complete_task(self, task_id: str, result: str = '') -> dict:
        """完成任务"""
        tasks = self._load_tasks()
        
        for task in tasks:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
                task['result'] = result
                
                # 更新 Agent 状态
                agent_name = task['agent']
                if agent_name in self.agents:
                    self.agents[agent_name]['status'] = 'available'
                    self.agents[agent_name]['current_task'] = None
                
                self._save_tasks(tasks)
                self._save_agents_status()
                
                return {'success': True, 'message': f'任务 {task_id} 已完成'}
        
        return {'success': False, 'message': f'任务不存在：{task_id}'}
    
    def get_agent_workload(self) -> dict:
        """获取 Agent 工作负载"""
        tasks = self._load_tasks()
        
        workload = {}
        for agent_name in self.agents:
            agent_tasks = [t for t in tasks if t['agent'] == agent_name and t['status'] in ['assigned', 'in_progress']]
            workload[agent_name] = {
                'active_tasks': len(agent_tasks),
                'status': self.agents[agent_name]['status'],
                'current_task': self.agents[agent_name].get('current_task')
            }
        
        return workload
    
    def get_task_status(self) -> dict:
        """获取任务状态概览"""
        tasks = self._load_tasks()
        
        status_count = {}
        for task in tasks:
            status = task['status']
            status_count[status] = status_count.get(status, 0) + 1
        
        return {
            'total': len(tasks),
            'by_status': status_count,
            'by_agent': self.get_agent_workload()
        }
    
    def _load_tasks(self) -> list:
        """加载任务列表"""
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_tasks(self, tasks: list):
        """保存任务列表"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    
    def _count_tasks(self) -> int:
        """计算任务总数"""
        return len(self._load_tasks())
    
    def list_agents(self) -> str:
        """列出所有 Agent 及其状态"""
        output = []
        output.append("=" * 70)
        output.append("🤖 Agent 列表及状态")
        output.append("=" * 70)
        
        workload = self.get_agent_workload()
        
        for name, info in self.agents.items():
            status_icon = "🟢" if info['status'] == 'available' else "🔴"
            tasks = workload.get(name, {}).get('active_tasks', 0)
            output.append(f"{status_icon} {name:<25} {info['status']:<12} 任务数：{tasks}")
        
        output.append("=" * 70)
        return "\n".join(output)


def main():
    """命令行入口"""
    import sys
    
    dispatcher = TaskDispatcher()
    
    if len(sys.argv) < 2:
        print("用法：python3 task_dispatcher.py <command> [args]")
        print("\n可用命令:")
        print("  list-agents                        列出所有 Agent")
        print("  assign <agent> <task> [priority]   分配任务")
        print("  complete <task_id>                 完成任务")
        print("  status                             查看任务状态")
        return
    
    command = sys.argv[1]
    
    if command == 'list-agents':
        print(dispatcher.list_agents())
    
    elif command == 'assign':
        if len(sys.argv) < 4:
            print("用法：assign <agent> <task> [priority]")
            return
        
        agent = sys.argv[2]
        task = sys.argv[3]
        priority = sys.argv[4] if len(sys.argv) > 4 else 'P1'
        
        result = dispatcher.assign_task(agent, task, priority)
        if result['success']:
            print(f"✅ {result['message']}")
            print(result['notification'])
        else:
            print(f"❌ {result['message']}")
    
    elif command == 'complete':
        if len(sys.argv) < 3:
            print("用法：complete <task_id>")
            return
        
        result = dispatcher.complete_task(sys.argv[2])
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")
    
    elif command == 'status':
        status = dispatcher.get_task_status()
        print("📊 任务状态概览")
        print(f"总任务数：{status['total']}")
        print("\n按状态统计:")
        for s, c in status['by_status'].items():
            print(f"  {s}: {c}")
        print("\n按 Agent 统计:")
        for agent, info in status['by_agent'].items():
            print(f"  {agent}: {info['active_tasks']} 个活跃任务")
    
    else:
        print(f"❌ 未知命令：{command}")


if __name__ == '__main__':
    main()

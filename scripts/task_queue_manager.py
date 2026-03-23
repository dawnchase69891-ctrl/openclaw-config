#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务队列管理器 - 带并发控制和超时监控

功能:
- 并发控制 (max_concurrent)
- 任务超时
- 优先级队列
- 监控告警

使用示例:
    from task_queue_manager import TaskQueueManager
    
    manager = TaskQueueManager(max_concurrent=5)
    
    # 提交任务
    await manager.spawn_with_control(
        agent_id='clawbuilder',
        task='实现登录功能',
        priority=1,
        timeout=300
    )
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


# ==================== 数据类 ====================

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class Task:
    """任务数据结构"""
    agent_id: str
    task: str
    priority: int = 1
    timeout: int = 300  # 5 分钟
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'agent_id': self.agent_id,
            'task': self.task,
            'priority': self.priority,
            'timeout': self.timeout,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status.value,
            'result': self.result,
            'error': self.error
        }


# ==================== 核心类 ====================

class TaskQueueManager:
    """任务队列管理器"""
    
    def __init__(self, max_concurrent: int = 5, state_file: str = None):
        """
        初始化任务队列管理器
        
        Args:
            max_concurrent: 最大并发数
            state_file: 状态持久化文件路径
        """
        self.max_concurrent = max_concurrent
        self.running = 0
        self.queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.lock = asyncio.Lock()
        self.active_tasks: Dict[str, Task] = {}
        
        # 状态持久化
        self.state_file = Path(state_file) if state_file else \
            Path.home() / '.openclaw' / 'workspace' / '.task-queue-state.json'
        
        # 监控配置
        self.alert_threshold_seconds = 600  # 10 分钟告警
        self.last_alert_time: Optional[datetime] = None
    
    async def _load_state(self):
        """加载持久化状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.running = state.get('running', 0)
                    for task_data in state.get('active_tasks', []):
                        task = Task(
                            agent_id=task_data['agent_id'],
                            task=task_data['task'],
                            priority=task_data['priority'],
                            timeout=task_data['timeout'],
                            created_at=datetime.fromisoformat(task_data['created_at']),
                            status=TaskStatus(task_data['status'])
                        )
                        self.active_tasks[task_data['agent_id']] = task
            except Exception as e:
                print(f"⚠️ 加载状态失败：{e}")
    
    async def _save_state(self):
        """保存持久化状态"""
        try:
            state = {
                'running': self.running,
                'active_tasks': [t.to_dict() for t in self.active_tasks.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存状态失败：{e}")
    
    async def enqueue(self, task: Task):
        """添加任务到队列"""
        await self.queue.put((-task.priority, task))
        await self._save_state()
    
    async def spawn_with_control(
        self,
        agent_id: str,
        task: str,
        priority: int = 1,
        timeout: int = 300
    ) -> Any:
        """
        带并发控制的任务执行
        
        Args:
            agent_id: Agent ID
            task: 任务内容
            priority: 优先级 (1-10, 越高越优先)
            timeout: 超时时间 (秒)
            
        Returns:
            Any: 任务结果
        """
        t = Task(agent_id, task, priority, timeout)
        
        async with self.lock:
            if self.running >= self.max_concurrent:
                print(f"⏳ 并发数已达上限 ({self.running}/{self.max_concurrent})，任务进入队列")
                await self.enqueue(t)
                while True:
                    await asyncio.sleep(1)
                    async with self.lock:
                        if self.running < self.max_concurrent:
                            break
                async with self.lock:
                    if self.running >= self.max_concurrent:
                        await self.enqueue(t)
                        return await self.spawn_with_control(agent_id, task, priority, timeout)
            
            self.running += 1
            self.active_tasks[agent_id] = t
            t.status = TaskStatus.RUNNING
            t.started_at = datetime.now()
        
        try:
            result = await asyncio.wait_for(
                self._execute_task(agent_id, task),
                timeout=timeout
            )
            
            t.status = TaskStatus.COMPLETED
            t.completed_at = datetime.now()
            t.result = result
            
            print(f"✅ 任务完成：{agent_id}")
            return result
            
        except asyncio.TimeoutError:
            t.status = TaskStatus.TIMEOUT
            t.error = f"任务超时 ({timeout}秒)"
            print(f"❌ 任务超时：{agent_id}")
            await self._send_alert(f"任务超时：{agent_id} - {task[:50]}")
            raise
            
        except Exception as e:
            t.status = TaskStatus.FAILED
            t.error = str(e)
            print(f"❌ 任务失败：{agent_id} - {e}")
            raise
            
        finally:
            async with self.lock:
                self.running -= 1
                if agent_id in self.active_tasks:
                    del self.active_tasks[agent_id]
                
                await self._save_state()
                
                if not self.queue.empty():
                    _, next_task = await self.queue.get()
                    asyncio.create_task(
                        self.spawn_with_control(
                            next_task.agent_id,
                            next_task.task,
                            next_task.priority,
                            next_task.timeout
                        )
                    )
    
    async def _execute_task(self, agent_id: str, task: str) -> Any:
        """
        实际执行任务 (封装 sessions_spawn)
        
        Args:
            agent_id: Agent ID
            task: 任务内容
            
        Returns:
            Any: 任务结果
        """
        import subprocess
        
        result = subprocess.run(
            ['openclaw', 'sessions', 'spawn', '--agent', agent_id, '--task', task],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise Exception(f"任务执行失败：{result.stderr}")
        
        return result.stdout
    
    async def _send_alert(self, message: str):
        """发送告警 (防抖动)"""
        now = datetime.now()
        
        if self.last_alert_time and (now - self.last_alert_time).seconds < 600:
            return
        
        self.last_alert_time = now
        print(f"🚨 告警：{message}")
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return {
            'running': self.running,
            'max_concurrent': self.max_concurrent,
            'queue_size': self.queue.qsize(),
            'active_tasks': len(self.active_tasks),
            'tasks': [t.to_dict() for t in self.active_tasks.values()]
        }
    
    async def monitor_long_running_tasks(self):
        """监控长时间运行的任务"""
        while True:
            await asyncio.sleep(60)
            
            now = datetime.now()
            for agent_id, task in list(self.active_tasks.items()):
                if task.started_at:
                    running_time = (now - task.started_at).seconds
                    
                    if running_time > self.alert_threshold_seconds:
                        await self._send_alert(
                            f"任务运行时间过长：{agent_id} "
                            f"({running_time}秒) - {task.task[:50]}"
                        )


# ==================== 命令行入口 ====================

async def main():
    """命令行入口"""
    import sys
    
    manager = TaskQueueManager()
    
    if len(sys.argv) < 2:
        print("用法：python3 task_queue_manager.py <command> [args]")
        print("\n可用命令:")
        print("  status              查看队列状态")
        print("  submit <agent> <task>  提交任务")
        print("  monitor             启动监控")
        return
    
    command = sys.argv[1]
    
    if command == 'status':
        status = await manager.get_queue_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif command == 'submit':
        if len(sys.argv) < 4:
            print("用法：submit <agent_id> <task>")
            return
        
        agent_id = sys.argv[2]
        task = ' '.join(sys.argv[3:])
        
        try:
            result = await manager.spawn_with_control(agent_id, task)
            print(f"✅ 任务提交成功")
        except Exception as e:
            print(f"❌ 任务提交失败：{e}")
    
    elif command == 'monitor':
        print("启动任务监控...")
        await manager.monitor_long_running_tasks()
    
    else:
        print(f"❌ 未知命令：{command}")


if __name__ == '__main__':
    asyncio.run(main())

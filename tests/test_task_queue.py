#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务队列管理器单元测试
"""

import pytest
import asyncio
from pathlib import Path
import sys
import json

# 添加项目路径
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
sys.path.insert(0, str(WORKSPACE / 'scripts'))

from task_queue_manager import (
    TaskQueueManager,
    Task,
    TaskStatus
)


@pytest.fixture
def manager(temp_dir):
    """创建任务队列管理器实例"""
    state_file = str(temp_dir / 'task-queue-state.json')
    return TaskQueueManager(max_concurrent=5, state_file=state_file)


@pytest.fixture
def temp_dir(tmp_path):
    """临时目录 fixture"""
    return tmp_path


class TestTaskDataStructure:
    """任务数据结构测试"""
    
    def test_task_creation(self):
        """测试任务创建"""
        task = Task(
            agent_id='clawbuilder',
            task='实现登录功能',
            priority=5,
            timeout=300
        )
        
        assert task.agent_id == 'clawbuilder'
        assert task.task == '实现登录功能'
        assert task.priority == 5
        assert task.timeout == 300
        assert task.status == TaskStatus.PENDING
    
    def test_task_to_dict(self):
        """测试任务序列化"""
        task = Task(
            agent_id='clawbuilder',
            task='test task',
            priority=3
        )
        
        data = task.to_dict()
        
        assert data['agent_id'] == 'clawbuilder'
        assert data['task'] == 'test task'
        assert data['priority'] == 3
        assert data['status'] == 'pending'
    
    def test_task_status_enum(self):
        """测试任务状态枚举"""
        assert TaskStatus.PENDING.value == 'pending'
        assert TaskStatus.RUNNING.value == 'running'
        assert TaskStatus.COMPLETED.value == 'completed'
        assert TaskStatus.FAILED.value == 'failed'
        assert TaskStatus.TIMEOUT.value == 'timeout'


class TestConcurrencyControl:
    """并发控制测试"""
    
    @pytest.mark.asyncio
    async def test_max_concurrent_limit(self, manager, mocker):
        """测试最大并发限制"""
        # Mock _execute_task 使其延迟返回
        async def mock_execute(agent_id, task):
            await asyncio.sleep(0.5)
            return 'done'
        
        mocker.patch.object(manager, '_execute_task', side_effect=mock_execute)
        
        # 提交 10 个任务
        tasks = [
            manager.spawn_with_control(f'agent_{i}', f'task_{i}', timeout=2)
            for i in range(10)
        ]
        
        # 等待一小段时间，让任务开始执行
        await asyncio.sleep(0.1)
        
        # 验证并发数不超过限制
        assert manager.running <= manager.max_concurrent
        
        # 等待所有任务完成
        await asyncio.gather(*tasks, return_exceptions=True)
    
    @pytest.mark.asyncio
    async def test_queue_enqueuing(self, manager, mocker):
        """测试任务队列"""
        # Mock _execute_task
        mocker.patch.object(manager, '_execute_task', return_value='done')
        
        # 先占满并发数
        manager.running = manager.max_concurrent
        
        # 创建任务
        task = Task(agent_id='test', task='test task', priority=5)
        
        # 加入队列
        await manager.enqueue(task)
        
        # 验证队列大小
        assert manager.queue.qsize() == 1


class TestTimeoutControl:
    """超时控制测试"""
    
    @pytest.mark.asyncio
    async def test_task_timeout(self, manager, mocker):
        """测试任务超时"""
        # Mock _execute_task 使其超时
        async def mock_timeout(agent_id, task):
            await asyncio.sleep(10)  # 超过 timeout
            return 'done'
        
        mocker.patch.object(manager, '_execute_task', side_effect=mock_timeout)
        
        # 提交短超时任务
        with pytest.raises(asyncio.TimeoutError):
            await manager.spawn_with_control(
                'agent_1',
                'timeout task',
                timeout=1  # 1 秒超时
            )
    
    @pytest.mark.asyncio
    async def test_task_timeout_status(self, manager, mocker):
        """测试超时任务状态"""
        async def mock_timeout(agent_id, task):
            await asyncio.sleep(10)
            return 'done'
        
        mocker.patch.object(manager, '_execute_task', side_effect=mock_timeout)
        
        try:
            await manager.spawn_with_control('agent_1', 'test', timeout=1)
        except asyncio.TimeoutError:
            pass
        
        # 验证任务状态为超时
        assert 'agent_1' not in manager.active_tasks  # 已清理


class TestPriorityQueue:
    """优先级队列测试"""
    
    @pytest.mark.asyncio
    async def test_priority_ordering(self, manager):
        """测试优先级排序"""
        # 创建不同优先级的任务
        task_low = Task(agent_id='agent_1', task='low', priority=1)
        task_high = Task(agent_id='agent_2', task='high', priority=10)
        task_mid = Task(agent_id='agent_3', task='mid', priority=5)
        
        # 按低到高顺序入队
        await manager.enqueue(task_low)
        await manager.enqueue(task_high)
        await manager.enqueue(task_mid)
        
        # 验证出队顺序 (高优先级先出)
        _, out1 = await manager.queue.get()
        _, out2 = await manager.queue.get()
        _, out3 = await manager.queue.get()
        
        assert out1.priority == 10  # 最高优先级
        assert out2.priority == 5
        assert out3.priority == 1


class TestStatePersistence:
    """状态持久化测试"""
    
    @pytest.mark.asyncio
    async def test_save_state(self, manager, temp_dir):
        """测试状态保存"""
        task = Task(agent_id='test', task='test task')
        manager.active_tasks['test'] = task
        manager.running = 1
        
        await manager._save_state()
        
        # 验证文件存在
        state_file = temp_dir / 'task-queue-state.json'
        assert state_file.exists()
        
        # 验证内容
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        assert state['running'] == 1
        assert len(state['active_tasks']) == 1
    
    @pytest.mark.asyncio
    async def test_load_state(self, manager, temp_dir):
        """测试状态加载"""
        # 先保存状态
        task = Task(agent_id='test', task='test task', priority=5)
        manager.active_tasks['test'] = task
        manager.running = 1
        await manager._save_state()
        
        # 创建新管理器
        state_file = temp_dir / 'task-queue-state.json'
        new_manager = TaskQueueManager(max_concurrent=5, state_file=str(state_file))
        
        # 加载状态
        await new_manager._load_state()
        
        # 验证状态恢复
        assert new_manager.running == 1
        assert 'test' in new_manager.active_tasks


class TestQueueStatus:
    """队列状态测试"""
    
    @pytest.mark.asyncio
    async def test_get_queue_status(self, manager):
        """测试获取队列状态"""
        task = Task(agent_id='test', task='test task')
        manager.active_tasks['test'] = task
        manager.running = 1
        
        status = await manager.get_queue_status()
        
        assert status['running'] == 1
        assert status['max_concurrent'] == 5
        assert status['active_tasks'] == 1
        assert len(status['tasks']) == 1


class TestAlertSystem:
    """告警系统测试"""
    
    @pytest.mark.asyncio
    async def test_alert_throttling(self, manager):
        """测试告警节流"""
        # 第一次告警
        await manager._send_alert('Test alert 1')
        first_alert_time = manager.last_alert_time
        
        # 立即第二次告警 (应该被抑制)
        await manager._send_alert('Test alert 2')
        
        # 验证两次告警时间相同 (第二次被抑制)
        assert manager.last_alert_time == first_alert_time


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

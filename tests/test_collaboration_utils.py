#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 collaboration_utils.py - Agent 协作工具
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch

# Python 3.7 兼容性处理
try:
    from unittest.mock import AsyncMock
except ImportError:
    from unittest.mock import MagicMock as AsyncMock

from collaboration_utils import (
    CollaborationService,
    AgentOfflineError,
    AgentBusyError,
    SessionSendError,
    DeadLetterMessage,
    AgentStatus,
    send_with_retry,
    get_collaboration_service
)


@pytest.fixture
def service(temp_dir):
    """创建协作服务实例"""
    return CollaborationService(dead_letter_path=str(temp_dir / 'dead-letter'))


class TestAgentStatus:
    """测试 Agent 状态检查"""
    
    @pytest.mark.asyncio
    async def test_get_agent_status_online(self, service, mock_sessions_list):
        """测试获取在线 Agent 状态"""
        status = await service.get_agent_status('main')
        assert status == AgentStatus.ONLINE
    
    @pytest.mark.asyncio
    async def test_get_agent_status_busy(self, service, mock_sessions_list):
        """测试获取繁忙 Agent 状态"""
        status = await service.get_agent_status('clawbuilder')
        assert status == AgentStatus.BUSY
    
    @pytest.mark.asyncio
    async def test_get_agent_status_offline(self, service):
        """测试获取离线 Agent 状态"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            status = await service.get_agent_status('offline_agent')
            assert status == AgentStatus.OFFLINE
    
    @pytest.mark.asyncio
    async def test_get_agent_status_error(self, service):
        """测试获取 Agent 状态异常"""
        with patch('subprocess.run', side_effect=Exception("Test error")):
            status = await service.get_agent_status('main')
            assert status == AgentStatus.UNKNOWN


class TestDelayCalculation:
    """测试延迟计算 (指数退避)"""
    
    def test_delay_increases(self, service):
        """测试延迟随尝试次数增加"""
        delay0 = service._calculate_delay(0)
        delay1 = service._calculate_delay(1)
        delay2 = service._calculate_delay(2)
        
        assert delay0 < delay1 < delay2
    
    def test_delay_respects_max(self, service):
        """测试延迟不超过最大值"""
        delay = service._calculate_delay(10)
        assert delay <= service.max_delay
    
    def test_delay_has_jitter(self, service):
        """测试延迟包含随机抖动"""
        delays = [service._calculate_delay(1) for _ in range(10)]
        # 抖动应该导致不同的延迟值
        assert len(set(delays)) > 1


class TestSendMessage:
    """测试消息发送"""
    
    @pytest.mark.asyncio
    async def test_send_with_retry_success(self, service, mocker):
        """测试发送成功场景"""
        # Mock _send_message 成功
        mocker.patch.object(service, '_send_message', return_value=True)
        
        result = await service.send_with_retry('main', 'test message')
        assert result == True
    
    @pytest.mark.asyncio
    async def test_send_with_retry_failure_then_success(self, service, mocker):
        """测试重试后成功"""
        # Mock 前两次失败，第三次成功
        mock_send = mocker.patch.object(service, '_send_message')
        mock_send.side_effect = [False, False, True]
        
        result = await service.send_with_retry('main', 'test message', max_retries=3)
        assert result == True
        assert mock_send.call_count == 3
    
    @pytest.mark.asyncio
    async def test_send_with_retry_all_failures(self, service, mocker, temp_dir):
        """测试所有重试失败"""
        # Mock _send_message 持续失败
        mocker.patch.object(service, '_send_message', side_effect=Exception('Failed'))
        
        with pytest.raises(Exception):
            await service.send_with_retry('offline_agent', 'test', max_retries=2)
        
        # 验证死信队列有记录
        dead_letters = await service.get_dead_letter_queue()
        assert len(dead_letters) > 0
        assert dead_letters[0].target == 'offline_agent'
    
    @pytest.mark.asyncio
    async def test_send_with_status_check_offline(self, service, mocker):
        """测试状态检查发现离线"""
        mocker.patch.object(service, 'get_agent_status', return_value=AgentStatus.OFFLINE)
        
        with pytest.raises(AgentOfflineError):
            await service.send_with_retry('offline_agent', 'test', check_status=True)
    
    @pytest.mark.asyncio
    async def test_send_with_status_check_busy(self, service, mocker):
        """测试状态检查发现繁忙"""
        mocker.patch.object(service, 'get_agent_status', return_value=AgentStatus.BUSY)
        
        with pytest.raises(AgentBusyError):
            await service.send_with_retry('busy_agent', 'test', check_status=True)


class TestDeadLetterQueue:
    """测试死信队列"""
    
    @pytest.mark.asyncio
    async def test_dead_letter_structure(self, service):
        """测试死信消息数据结构"""
        dead_letter = DeadLetterMessage(
            target='test_agent',
            message='test message',
            error_type='TestError',
            error_message='Test failed',
            attempts=3,
            failed_at='2026-03-23T10:00:00'
        )
        
        data = dead_letter.to_dict()
        assert data['target'] == 'test_agent'
        assert data['error_type'] == 'TestError'
        assert data['attempts'] == 3
    
    @pytest.mark.asyncio
    async def test_dead_letter_persistence(self, service, temp_dir):
        """测试死信消息持久化"""
        dead_letter = DeadLetterMessage(
            target='test_agent',
            message='test message',
            error_type='TestError',
            error_message='Test failed',
            attempts=3,
            failed_at='2026-03-23T10:00:00'
        )
        
        await service._enqueue_dead_letter(dead_letter)
        
        # 验证文件已创建
        files = list(temp_dir.glob('dead-letter/*.json'))
        assert len(files) == 1


class TestGlobalService:
    """测试全局服务实例"""
    
    def test_get_collaboration_service_singleton(self):
        """测试全局服务是单例"""
        service1 = get_collaboration_service()
        service2 = get_collaboration_service()
        assert service1 is service2
    
    @pytest.mark.asyncio
    async def test_send_with_retry_function(self, mocker):
        """测试便捷函数 send_with_retry"""
        mock_service = AsyncMock()
        mock_service.send_with_retry.return_value = True
        
        with patch('collaboration_utils._collaboration_service', mock_service):
            result = await send_with_retry('main', 'test')
            assert result == True

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 feishu_notifier.py - 飞书通知集成
"""

import pytest
import os
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from feishu_notifier import (
    FeishuNotifier,
    NotificationConfig,
    NotificationType,
    send_alert,
    send_task_complete,
    send_error_report,
    get_notifier
)


@pytest.fixture
def mock_config():
    """Mock 通知配置"""
    return NotificationConfig(
        webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/test",
        secret="test_secret"
    )


@pytest.fixture
def notifier(mock_config):
    """创建通知器实例"""
    return FeishuNotifier(config=mock_config)


class TestSignatureGeneration:
    """测试签名生成"""
    
    def test_generate_signature(self, notifier):
        """测试签名生成正确性"""
        timestamp = "1234567890"
        signature = notifier._generate_signature(timestamp)
        
        # 签名应该是 Base64 编码的字符串
        assert isinstance(signature, str)
        assert len(signature) > 0
    
    def test_generate_signature_without_secret(self, temp_dir):
        """测试无密钥时不生成签名"""
        config = NotificationConfig(
            webhook_url="https://example.com/webhook",
            secret=None
        )
        notifier = FeishuNotifier(config=config)
        signature = notifier._generate_signature("1234567890")
        assert signature == ""


class TestMessageDeduplication:
    """测试消息去重"""
    
    def test_should_send_first_time(self, notifier):
        """测试首次发送应该成功"""
        message_key = "test_message_1"
        assert notifier._should_send(message_key) == True
    
    def test_should_send_duplicate(self, notifier):
        """测试重复消息应该被阻止"""
        message_key = "test_message_2"
        
        # 第一次发送
        assert notifier._should_send(message_key) == True
        
        # 第二次发送 (短时间内)
        assert notifier._should_send(message_key) == False
    
    def test_should_send_after_window(self, notifier):
        """测试超过时间窗口后可以重新发送"""
        message_key = "test_message_3"
        
        # 第一次发送
        notifier._should_send(message_key)
        
        # 模拟时间流逝 (超过 5 分钟)
        notifier.sent_messages[message_key] = time.time() - 301
        
        # 应该可以再次发送
        assert notifier._should_send(message_key) == True
    
    def test_generate_message_key_consistency(self, notifier):
        """测试消息 key 生成一致性"""
        content = "test content"
        key1 = notifier._generate_message_key(content)
        key2 = notifier._generate_message_key(content)
        assert key1 == key2
    
    def test_generate_message_key_uniqueness(self, notifier):
        """测试不同内容生成不同 key"""
        key1 = notifier._generate_message_key("content 1")
        key2 = notifier._generate_message_key("content 2")
        assert key1 != key2


class TestMessageBuilding:
    """测试消息构建"""
    
    def test_build_interactive_card(self, notifier):
        """测试构建交互式卡片"""
        import json
        
        card = notifier._build_interactive_card(
            title="Test Title",
            content="Test Content",
            color="red"
        )
        
        assert card["msg_type"] == "interactive"
        assert "card" in card
        
        card_data = json.loads(card["card"])  # 解析 JSON 字符串
        assert card_data["header"]["title"]["content"] == "Test Title"
    
    def test_build_interactive_card_with_mention(self, notifier):
        """测试构建带@的卡片"""
        import json
        
        card = notifier._build_interactive_card(
            title="Test",
            content="Content",
            mention_users=["ou_test123"]
        )
        
        card_data = json.loads(card["card"])
        assert "mention_list" in card_data["elements"]
    
    def test_build_text_message(self, notifier):
        """测试构建文本消息"""
        message = notifier._build_text_message(
            content="Test content"
        )
        
        assert message["msg_type"] == "text"
        assert "content" in message
    
    def test_build_text_message_with_mention(self, notifier):
        """测试构建带@的文本消息"""
        message = notifier._build_text_message(
            content="Test",
            mention_users=["ou_test123"]
        )
        
        content_data = eval(message["content"])
        assert "<at user_id='ou_test123'></at>" in content_data["text"]


class TestNotificationTypes:
    """测试不同类型通知"""
    
    @pytest.mark.asyncio
    async def test_send_alert(self, notifier, mock_feishu_webhook):
        """测试发送告警"""
        result = await notifier.send_alert(
            alert_title="Test Alert",
            alert_content="Something went wrong"
        )
        assert result == True
    
    @pytest.mark.asyncio
    async def test_send_task_complete(self, notifier, mock_feishu_webhook):
        """测试发送任务完成通知"""
        result = await notifier.send_task_complete(
            task_id="TASK-001",
            assignee="ClawBuilder",
            task_description="Implement login feature",
            duration="2h 30m"
        )
        assert result == True
    
    @pytest.mark.asyncio
    async def test_send_task_failed(self, notifier, mock_feishu_webhook):
        """测试发送任务失败通知"""
        result = await notifier.send_task_failed(
            task_id="TASK-002",
            assignee="ClawBuilder",
            task_description="Implement logout",
            error_message="Connection timeout"
        )
        assert result == True
    
    @pytest.mark.asyncio
    async def test_send_error_report(self, notifier, mock_feishu_webhook):
        """测试发送错误报告"""
        result = await notifier.send_error_report(
            module="Sync Script",
            error_type="ConnectionError",
            error_message="Failed to connect",
            stack_trace="Traceback..."
        )
        assert result == True
    
    @pytest.mark.asyncio
    async def test_send_info(self, notifier, mock_feishu_webhook):
        """测试发送普通信息"""
        result = await notifier.send_info(
            title="Info Title",
            content="Info content"
        )
        assert result == True


class TestSendMethod:
    """测试通用发送方法"""
    
    @pytest.mark.asyncio
    async def test_send_with_card(self, notifier, mock_feishu_webhook):
        """测试发送卡片消息"""
        result = await notifier.send(
            title="Test",
            content="Content",
            use_card=True
        )
        assert result == True
    
    @pytest.mark.asyncio
    async def test_send_without_card(self, notifier, mock_feishu_webhook):
        """测试发送文本消息"""
        result = await notifier.send(
            title="Test",
            content="Content",
            use_card=False
        )
        assert result == True
    
    @pytest.mark.asyncio
    async def test_send_deduplication(self, notifier, mock_feishu_webhook):
        """测试发送去重"""
        # 第一次发送
        result1 = await notifier.send(
            title="Test",
            content="Same content"
        )
        assert result1 == True
        
        # 第二次发送 (相同内容，应该被去重)
        result2 = await notifier.send(
            title="Test",
            content="Same content"
        )
        assert result2 == False


class TestGlobalNotifier:
    """测试全局通知器"""
    
    def test_get_notifier_without_config(self):
        """测试无配置时获取通知器"""
        # 清除环境变量
        old_value = os.environ.pop('FEISHU_WEBHOOK_URL', None)
        
        try:
            notifier = get_notifier()
            assert notifier is None
        finally:
            # 恢复环境变量
            if old_value:
                os.environ['FEISHU_WEBHOOK_URL'] = old_value
    
    def test_send_alert_function(self, mocker):
        """测试便捷函数 send_alert"""
        mock_notifier = mocker.MagicMock()
        mock_notifier.send_alert.return_value = True
        
        with patch('feishu_notifier._notifier', mock_notifier):
            result = send_alert("Title", "Content")
            assert result == True
    
    def test_send_task_complete_function(self, mocker):
        """测试便捷函数 send_task_complete"""
        mock_notifier = mocker.MagicMock()
        mock_notifier.send_task_complete.return_value = True
        
        with patch('feishu_notifier._notifier', mock_notifier):
            result = send_task_complete("TASK-001", "User", "Desc")
            assert result == True
    
    def test_send_error_report_function(self, mocker):
        """测试便捷函数 send_error_report"""
        mock_notifier = mocker.MagicMock()
        mock_notifier.send_error_report.return_value = True
        
        with patch('feishu_notifier._notifier', mock_notifier):
            result = send_error_report("Module", "Error", "Message")
            assert result == True

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 config_sync.py - 配置同步脚本
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from sync_feishu_to_openclaw import (
    ConfigSyncService,
    WORKSPACE,
    AGENT_CONFIG_SCHEMA
)


@pytest.fixture
def service(temp_dir):
    """创建配置同步服务实例"""
    # 设置测试用的目录
    service = ConfigSyncService()
    service.config_dir = temp_dir / 'config'
    service.backup_dir = temp_dir / 'backup'
    service.agent_config_dir = temp_dir / 'agents'
    
    # 创建目录
    service.config_dir.mkdir(parents=True, exist_ok=True)
    service.backup_dir.mkdir(parents=True, exist_ok=True)
    service.agent_config_dir.mkdir(parents=True, exist_ok=True)
    
    return service


@pytest.fixture
def sample_agents():
    """示例 Agent 配置列表"""
    return [
        {
            "agent_id": "main",
            "name": "Main Agent",
            "systemPrompt": "You are the main agent",
            "skills": ["skill1", "skill2"],
            "model": "default"
        },
        {
            "agent_id": "clawbuilder",
            "name": "ClawBuilder",
            "systemPrompt": "You are a developer",
            "skills": ["coding"],
            "model": "default"
        }
    ]


class TestConfigValidation:
    """测试配置验证"""
    
    def test_validate_valid_config(self, service, sample_agents):
        """测试验证有效配置"""
        result = service.validate_config(sample_agents)
        assert result == True
    
    def test_validate_missing_required_field(self, service):
        """测试验证缺少必需字段"""
        invalid_agents = [
            {
                "agent_id": "test",
                "name": "Test"
                # 缺少 systemPrompt
            }
        ]
        
        with pytest.raises(Exception):
            service.validate_config(invalid_agents)
    
    def test_validate_wrong_type(self, service):
        """测试验证错误类型"""
        invalid_agents = [
            {
                "agent_id": 123,  # 应该是字符串
                "name": "Test",
                "systemPrompt": "Test"
            }
        ]
        
        with pytest.raises(Exception):
            service.validate_config(invalid_agents)


class TestBackup:
    """测试备份功能"""
    
    def test_backup_current_config(self, service, sample_agents):
        """测试备份当前配置"""
        # 先创建一些配置
        service.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = service.config_dir / 'test.json'
        config_file.write_text(json.dumps({"test": "data"}))
        
        # 执行备份
        backup_path = service.backup_current_config()
        
        # 验证备份目录已创建
        assert Path(backup_path).exists()
        assert (Path(backup_path) / 'test.json').exists()
    
    def test_backup_empty_config(self, service):
        """测试备份空配置目录"""
        backup_path = service.backup_current_config()
        assert Path(backup_path).exists()


class TestWriteConfigs:
    """测试写入配置"""
    
    def test_write_agent_configs(self, service, sample_agents):
        """测试写入 Agent 配置"""
        # 创建主配置文件
        main_config = service.workspace / 'config.json'
        main_config.parent.mkdir(parents=True, exist_ok=True)
        main_config.write_text('{}')
        
        # 写入配置
        service.write_agent_configs(sample_agents)
        
        # 验证主配置已更新
        with open(main_config, 'r') as f:
            config = json.load(f)
        
        assert 'agents' in config
        assert 'list' in config['agents']
        assert len(config['agents']['list']) == 2
        assert 'main' in config['agents']['list']
        assert 'clawbuilder' in config['agents']['list']
        
        # 验证 Agent 配置文件已创建
        assert (service.agent_config_dir / 'main.json').exists()
        assert (service.agent_config_dir / 'clawbuilder.json').exists()
        
        # 验证 Agent 配置内容
        with open(service.agent_config_dir / 'main.json', 'r') as f:
            main_agent = json.load(f)
        
        assert main_agent['agent_id'] == 'main'
        assert main_agent['name'] == 'Main Agent'


class TestCleanupImagePlaceholders:
    """测试清理图片占位符"""
    
    def test_cleanup_image_placeholders(self, service, temp_dir):
        """测试清理图片占位符"""
        # 创建测试文档
        docs_dir = temp_dir / 'docs'
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = docs_dir / 'test.md'
        test_file.write_text("""
# Test Document

This is a test image[[image123]] in the document.

Another image[[image456]] here.
""")
        
        # 临时修改 service 的 workspace
        service.workspace = temp_dir
        service.cleanup_image_placeholders()
        
        # 验证占位符已被清理
        content = test_file.read_text()
        assert 'image[[' not in content
        assert '[图片已移除]' in content
    
    def test_cleanup_no_placeholders(self, service, temp_dir):
        """测试没有占位符的文件"""
        docs_dir = temp_dir / 'docs'
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = docs_dir / 'test.md'
        test_file.write_text("# Test\n\nNo images here.")
        
        service.workspace = temp_dir
        service.cleanup_image_placeholders()
        
        content = test_file.read_text()
        assert content == "# Test\n\nNo images here."


class TestGitOperations:
    """测试 Git 操作"""
    
    def test_git_commit_and_push(self, service, mocker):
        """测试 Git 提交和推送"""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value.returncode = 0
        
        service.git_commit_and_push("Test commit")
        
        assert mock_run.call_count == 3
        calls = [call[0][0] for call in mock_run.call_args_list]
        assert calls[0][:3] == ['git', 'add', '-A']
        assert calls[1][:2] == ['git', 'commit']
        assert calls[2][:2] == ['git', 'push']
    
    def test_git_commit_failure(self, service, mocker):
        """测试 Git 提交失败"""
        mock_run = mocker.patch('subprocess.run')
        mock_run.side_effect = Exception("Git failed")
        
        # 不应该抛出异常
        service.git_commit_and_push("Test commit")


class TestRestoreFromBackup:
    """测试从备份恢复"""
    
    def test_restore_from_backup(self, service, temp_dir):
        """测试从备份恢复配置"""
        # 创建备份
        backup_dir = service.backup_dir / '2026-03-23_10-00-00'
        backup_dir.mkdir(parents=True, exist_ok=True)
        (backup_dir / 'config.json').write_text('{"restored": true}')
        
        # 创建当前配置 (将被覆盖)
        service.config_dir.mkdir(parents=True, exist_ok=True)
        (service.config_dir / 'config.json').write_text('{"current": true}')
        
        # 恢复备份
        service.restore_from_backup()
        
        # 验证已恢复
        with open(service.config_dir / 'config.json', 'r') as f:
            config = json.load(f)
        
        assert config == {"restored": true}


class TestSync:
    """测试完整同步流程"""
    
    def test_sync_success(self, service, sample_agents, mocker):
        """测试成功同步"""
        # Mock 各个步骤
        mocker.patch.object(service, 'fetch_feishu_bitable', return_value=sample_agents)
        mocker.patch.object(service, 'validate_config', return_value=True)
        mocker.patch.object(service, 'backup_current_config', return_value='/tmp/backup')
        mocker.patch.object(service, 'write_agent_configs')
        mocker.patch.object(service, 'cleanup_image_placeholders')
        mocker.patch.object(service, 'git_commit_and_push')
        
        # 创建主配置文件
        main_config = service.workspace / 'config.json'
        main_config.parent.mkdir(parents=True, exist_ok=True)
        main_config.write_text('{}')
        
        # 执行同步
        result = service.sync()
        
        assert result == True
    
    def test_sync_validation_failure(self, service, mocker):
        """测试验证失败"""
        mocker.patch.object(service, 'fetch_feishu_bitable', return_value=[{"invalid": "data"}])
        mocker.patch.object(service, 'validate_config', side_effect=Exception("Validation failed"))
        mocker.patch.object(service, 'restore_from_backup')
        
        result = service.sync()
        assert result == False
    
    def test_sync_with_rollback(self, service, mocker):
        """测试同步失败后回滚"""
        mocker.patch.object(service, 'fetch_feishu_bitable', side_effect=Exception("API Error"))
        mock_restore = mocker.patch.object(service, 'restore_from_backup')
        
        result = service.sync()
        
        assert result == False
        mock_restore.assert_called_once()


class TestFeishuAPI:
    """测试飞书 API 调用"""
    
    def test_fetch_feishu_bitable_success(self, service, mock_feishu_api):
        """测试成功获取飞书数据"""
        # 设置环境变量
        os.environ['FEISHU_APP_ID'] = 'test_app_id'
        os.environ['FEISHU_APP_SECRET'] = 'test_app_secret'
        os.environ['FEISHU_BITABLE_TOKEN'] = 'test_token'
        
        agents = service.fetch_feishu_bitable()
        
        assert len(agents) == 1
        assert agents[0]['agent_id'] == 'main'
        
        # 清理环境变量
        del os.environ['FEISHU_APP_ID']
        del os.environ['FEISHU_APP_SECRET']
        del os.environ['FEISHU_BITABLE_TOKEN']
    
    def test_fetch_feishu_bitable_missing_credentials(self, service):
        """测试缺少飞书凭证"""
        # 确保环境变量未设置
        os.environ.pop('FEISHU_APP_ID', None)
        os.environ.pop('FEISHU_APP_SECRET', None)
        
        with pytest.raises(ValueError, match="缺少飞书 API 凭证"):
            service.fetch_feishu_bitable()

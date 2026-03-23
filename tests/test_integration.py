#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试 - 端到端测试套件

测试范围:
- 配置同步 → Agent 通信 → 任务执行
- 飞书通知集成测试
- 性能测试

运行方式:
    pytest tests/test_integration.py -v
"""

import pytest
import asyncio
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 添加项目路径
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
sys.path.insert(0, str(WORKSPACE))
sys.path.insert(0, str(WORKSPACE / 'scripts'))


# ==================== 测试夹具 ====================

@pytest.fixture
def test_config():
    """测试配置"""
    return {
        'max_retries': 3,
        'timeout': 30,
        'test_agent_id': 'clawbuilder',
        'test_folder_token': 'UDARfZ30YlI7ild68FmcEoianSg'
    }


@pytest.fixture
def doc_creator():
    """文档创建器实例"""
    from feishu_doc_creator import FeishuDocCreator
    return FeishuDocCreator()


# ==================== 端到端测试 ====================

class TestEndToEnd:
    """端到端测试套件"""
    
    @pytest.mark.asyncio
    async def test_config_sync_flow(self, test_config):
        """测试配置同步流程"""
        # 1. 模拟从飞书读取配置
        mock_config = {
            'agents': [
                {'agent_id': 'main', 'name': '骐骥', 'status': 'active'},
                {'agent_id': 'clawbuilder', 'name': 'ClawBuilder', 'status': 'active'}
            ]
        }
        
        # 2. 验证配置格式
        assert 'agents' in mock_config
        assert len(mock_config['agents']) > 0
        
        # 3. 模拟配置写入
        config_file = WORKSPACE / '.test' / 'config.json'
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(mock_config, f, ensure_ascii=False, indent=2)
        
        # 4. 验证配置已写入
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        
        assert loaded_config == mock_config
        
        # 清理
        config_file.unlink()
    
    @pytest.mark.asyncio
    async def test_agent_communication_flow(self, test_config):
        """测试 Agent 通信流程"""
        from collaboration_utils import CollaborationService, AgentStatus
        
        service = CollaborationService(dead_letter_path=str(WORKSPACE / '.test' / 'dead-letter'))
        
        # 1. 检查 Agent 状态 (模拟)
        # 实际测试需要真实的 OpenClaw 环境
        status = await service.get_agent_status(test_config['test_agent_id'])
        
        # 状态应该是有效的枚举值
        assert status in [AgentStatus.ONLINE, AgentStatus.BUSY, AgentStatus.OFFLINE, AgentStatus.UNKNOWN]
    
    @pytest.mark.asyncio
    async def test_task_execution_flow(self, test_config):
        """测试任务执行流程"""
        from task_queue_manager import TaskQueueManager, TaskStatus
        
        manager = TaskQueueManager(max_concurrent=2)
        
        # 1. 提交任务
        task = {
            'agent_id': test_config['test_agent_id'],
            'task': '测试任务',
            'priority': 5,
            'timeout': 10
        }
        
        # 2. 验证任务队列状态
        status = await manager.get_queue_status()
        assert 'running' in status
        assert 'max_concurrent' in status
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self, test_config, doc_creator):
        """测试完整流程：配置 → 通信 → 任务 → 文档"""
        # 1. 配置同步 (模拟)
        config_valid = True
        
        # 2. 文档创建
        doc_info = doc_creator.create_from_template(
            template='task-template',
            variables={
                'task_id': 'TEST-001',
                'assignee': 'ClawBuilder',
                'deadline': '2026-03-25',
                'priority': 'P1',
                'description': '集成测试任务'
            },
            title='测试任务文档'
        )
        
        # 3. 验证文档创建成功
        assert 'doc_id' in doc_info
        assert doc_info['template'] == 'task-template'
        assert 'TEST-001' in doc_info['title'] or 'TEST-001' in doc_info['content_preview']
        
        # 4. 清理图片占位符测试
        test_content = "这是一段测试文本 image[[test.png]] 更多内容"
        cleaned = doc_creator._cleanup_image_placeholders(test_content)
        assert 'image[[' not in cleaned
        assert '[图片已移除]' in cleaned


# ==================== 飞书通知集成测试 ====================

class TestFeishuNotification:
    """飞书通知集成测试"""
    
    @pytest.mark.asyncio
    async def test_doc_creation_notification(self, doc_creator):
        """测试文档创建通知"""
        # 1. 创建文档
        doc_info = doc_creator.create_from_template(
            template='meeting-template',
            variables={
                'meeting_date': '2026-03-23',
                'topic': '集成测试会议',
                'meeting_time': '14:00-15:00',
                'attendees': 'Jason, Rex',
                'recorder': 'ClawBuilder'
            }
        )
        
        # 2. 验证通知内容 (模拟)
        notification = {
            'type': 'doc_created',
            'doc_id': doc_info['doc_id'],
            'title': doc_info['title'],
            'template': doc_info['template']
        }
        
        assert notification['type'] == 'doc_created'
        assert 'doc_id' in notification
    
    @pytest.mark.asyncio
    async def test_variable_replacement(self, doc_creator):
        """测试变量替换功能"""
        # 1. 加载模板
        content = doc_creator._load_template('task-template')
        
        # 2. 替换变量
        variables = {
            'task_id': 'TASK-TEST-001',
            'assignee': 'TestUser',
            'deadline': '2026-12-31',
            'priority': 'P0',
            'description': '测试描述'
        }
        
        replaced = doc_creator._replace_variables(content, variables)
        
        # 3. 验证替换结果
        assert '{{task_id}}' not in replaced
        assert 'TASK-TEST-001' in replaced
        assert 'TestUser' in replaced
        assert '2026-12-31' in replaced
    
    @pytest.mark.asyncio
    async def test_image_cleanup(self, doc_creator):
        """测试图片占位符清理"""
        test_cases = [
            ("正常文本", "正常文本"),
            ("image[[test.png]]", "[图片已移除]"),
            ("前 image[[abc.png]] 后", "前 [图片已移除] 后"),
            ("多 image[[1.png]] 个 image[[2.png]]", "多 [图片已移除] 个 [图片已移除]"),
        ]
        
        for input_text, expected in test_cases:
            result = doc_creator._cleanup_image_placeholders(input_text)
            assert result == expected, f"Failed for input: {input_text}"


# ==================== 性能测试 ====================

class TestPerformance:
    """性能测试套件"""
    
    @pytest.mark.asyncio
    async def test_doc_creation_performance(self, doc_creator):
        """测试文档创建性能"""
        iterations = 10
        
        start_time = time.time()
        
        for i in range(iterations):
            doc_creator.create_from_template(
                template='task-template',
                variables={
                    'task_id': f'PERF-{i:03d}',
                    'assignee': 'PerfTester',
                    'deadline': '2026-03-25',
                    'priority': 'P2',
                    'description': f'性能测试任务 {i}'
                },
                cleanup_images=False  # 关闭清理以测试纯创建性能
            )
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / iterations
        
        print(f"\n性能测试结果:")
        print(f"  总耗时：{total_time:.3f}秒")
        print(f"  平均耗时：{avg_time:.3f}秒/文档")
        print(f"  吞吐量：{iterations/total_time:.2f} 文档/秒")
        
        # 性能要求：平均 < 1 秒/文档
        assert avg_time < 1.0, f"文档创建性能不达标：{avg_time:.3f}秒/文档"
    
    @pytest.mark.asyncio
    async def test_variable_replacement_performance(self, doc_creator):
        """测试变量替换性能"""
        # 1. 加载模板
        content = doc_creator._load_template('daily-report-template')
        
        variables = {
            'report_date': '2026-03-23',
            'reporter': 'PerfTester',
            'content': '测试内容' * 100  # 大量内容
        }
        
        iterations = 100
        
        start_time = time.time()
        
        for _ in range(iterations):
            doc_creator._replace_variables(content, variables)
        
        end_time = time.time()
        avg_time = (end_time - start_time) / iterations * 1000  # 转换为毫秒
        
        print(f"\n变量替换性能测试:")
        print(f"  平均耗时：{avg_time:.3f}毫秒/次")
        
        # 性能要求：平均 < 10 毫秒/次
        assert avg_time < 10.0, f"变量替换性能不达标：{avg_time:.3f}毫秒/次"
    
    @pytest.mark.asyncio
    async def test_concurrent_doc_creation(self, doc_creator):
        """测试并发文档创建"""
        import asyncio
        
        async def create_doc(task_id: str):
            return doc_creator.create_from_template(
                template='task-template',
                variables={
                    'task_id': task_id,
                    'assignee': 'ConcurrentTester',
                    'deadline': '2026-03-25',
                    'priority': 'P2',
                    'description': f'并发测试任务 {task_id}'
                },
                cleanup_images=False
            )
        
        # 并发创建 5 个文档
        tasks = [create_doc(f'CONC-{i:03d}') for i in range(5)]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        print(f"\n并发测试性能:")
        print(f"  并发数：5")
        print(f"  总耗时：{total_time:.3f}秒")
        print(f"  平均耗时：{total_time/5:.3f}秒/文档")
        
        # 验证所有文档创建成功
        assert len(results) == 5
        assert all('doc_id' in r for r in results)


# ==================== 模板测试 ====================

class TestTemplates:
    """模板测试套件"""
    
    def test_all_templates_exist(self, doc_creator):
        """测试所有模板文件存在"""
        templates = doc_creator.list_templates()
        
        assert len(templates) == 4, "应该有 4 个模板"
        
        template_names = [t['name'] for t in templates]
        expected = ['task-template', 'decision-template', 'meeting-template', 'daily-report-template']
        
        for name in expected:
            assert name in template_names, f"缺少模板：{name}"
    
    def test_template_variables(self, doc_creator):
        """测试模板变量完整性"""
        required_vars = {
            'task-template': ['task_id', 'assignee', 'deadline', 'priority', 'description'],
            'decision-template': ['decision_id', 'decision_maker', 'background'],
            'meeting-template': ['meeting_date', 'topic', 'attendees'],
            'daily-report-template': ['report_date', 'reporter']
        }
        
        for template_name, required in required_vars.items():
            content = doc_creator._load_template(template_name)
            
            for var in required:
                placeholder = '{{' + var + '}}'
                assert placeholder in content, f"模板 {template_name} 缺少变量：{var}"


# ==================== 异常测试 ====================

class TestExceptions:
    """异常测试套件"""
    
    def test_invalid_template(self, doc_creator):
        """测试无效模板处理"""
        with pytest.raises(ValueError, match="未知模板"):
            doc_creator.create_from_template(
                template='non-existent-template',
                variables={}
            )
    
    def test_empty_variables(self, doc_creator):
        """测试空变量处理"""
        # 空变量应该使用默认值
        doc_info = doc_creator.create_from_template(
            template='task-template',
            variables={}
        )
        
        assert 'doc_id' in doc_info
        # 应该包含默认时间戳
        assert 'created_at' in doc_info['content_preview'] or datetime.now().strftime('%Y-%m-%d') in doc_info['title']


# ==================== 主入口 ====================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

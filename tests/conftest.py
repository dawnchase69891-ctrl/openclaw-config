#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest 配置文件
"""

import pytest
import sys
from pathlib import Path

# 添加项目路径
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
sys.path.insert(0, str(WORKSPACE))
sys.path.insert(0, str(WORKSPACE / 'scripts'))


@pytest.fixture
def temp_dir(tmp_path):
    """临时目录 fixture"""
    return tmp_path


@pytest.fixture
def mock_sessions_list(mocker):
    """Mock sessions_list 命令"""
    mock_data = [
        {'agent_id': 'main', 'is_processing': False},
        {'agent_id': 'clawbuilder', 'is_processing': True},
    ]
    mocker.patch('subprocess.run', return_value=type('obj', (object,), {
        'returncode': 0,
        'stdout': str(mock_data)
    }))
    return mock_data

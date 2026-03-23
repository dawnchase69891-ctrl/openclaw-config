#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置验证脚本 - 验证 OpenClaw 配置文件的正确性

功能:
- 验证 config.json 格式
- 验证 Agent 配置文件
- 检查必要字段
- 输出验证报告

使用:
    python3 validate_config.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime


# ==================== 配置 ====================

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
CONFIG_FILE = WORKSPACE / 'config.json'
AGENT_CONFIG_DIR = WORKSPACE / 'agents'


# ==================== 验证逻辑 ====================

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
    
    def validate_main_config(self) -> bool:
        """验证主配置文件"""
        if not CONFIG_FILE.exists():
            self.errors.append(f"主配置文件不存在：{CONFIG_FILE}")
            return False
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"config.json JSON 格式错误：{e}")
            return False
        
        # 检查必要字段
        required_fields = ['agents']
        for field in required_fields:
            if field not in config:
                self.errors.append(f"缺少必要字段：{field}")
        
        # 检查 agents.list
        if 'agents' in config:
            if 'list' not in config['agents']:
                self.errors.append("agents.list 字段缺失")
            elif not isinstance(config['agents']['list'], list):
                self.errors.append("agents.list 必须是数组")
            else:
                self.info.append(f"已配置 {len(config['agents']['list'])} 个 Agent")
        
        # 检查插件配置一致性
        if 'plugins' in config:
            allow_list = config['plugins'].get('allow', [])
            entries = config['plugins'].get('entries', {})
            
            for plugin_name in entries:
                if entries[plugin_name].get('enabled', False):
                    if plugin_name not in allow_list:
                        self.errors.append(
                            f"插件配置不一致：{plugin_name} 已启用但不在 allow 列表中"
                        )
        
        return len(self.errors) == 0
    
    def validate_agent_configs(self) -> bool:
        """验证 Agent 配置文件"""
        if not AGENT_CONFIG_DIR.exists():
            self.warnings.append(f"Agent 配置目录不存在：{AGENT_CONFIG_DIR}")
            return True
        
        agent_files = list(AGENT_CONFIG_DIR.glob('*.json'))
        
        if not agent_files:
            self.warnings.append("未找到 Agent 配置文件")
            return True
        
        valid_count = 0
        for agent_file in agent_files:
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    agent = json.load(f)
                
                # 检查必要字段
                required = ['agent_id', 'name', 'systemPrompt']
                missing = [f for f in required if f not in agent]
                
                if missing:
                    self.errors.append(
                        f"{agent_file.name} 缺少字段：{', '.join(missing)}"
                    )
                else:
                    valid_count += 1
                
            except json.JSONDecodeError as e:
                self.errors.append(f"{agent_file.name} JSON 格式错误：{e}")
        
        self.info.append(f"验证了 {len(agent_files)} 个 Agent 配置，{valid_count} 个有效")
        return len(self.errors) == 0
    
    def validate_config_consistency(self) -> bool:
        """验证配置一致性"""
        # 检查主配置中的 agents.list 与实际 Agent 文件是否一致
        if not CONFIG_FILE.exists():
            return False
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        declared_agents = set(config.get('agents', {}).get('list', []))
        actual_agents = set()
        
        if AGENT_CONFIG_DIR.exists():
            for agent_file in AGENT_CONFIG_DIR.glob('*.json'):
                try:
                    with open(agent_file, 'r', encoding='utf-8') as f:
                        agent = json.load(f)
                        actual_agents.add(agent.get('agent_id', ''))
                except:
                    pass
        
        # 检查差异
        missing_files = declared_agents - actual_agents
        extra_files = actual_agents - declared_agents
        
        if missing_files:
            self.warnings.append(
                f"声明了但未找到配置文件的 Agent: {', '.join(missing_files)}"
            )
        
        if extra_files:
            self.warnings.append(
                f"有配置文件但未在 config.json 中声明的 Agent: {', '.join(extra_files)}"
            )
        
        return True
    
    def validate_all(self) -> bool:
        """执行所有验证"""
        print("🔍 开始验证配置...")
        print()
        
        # 1. 验证主配置
        print("1. 验证主配置文件...")
        main_valid = self.validate_main_config()
        print(f"   {'✅' if main_valid else '❌'} 主配置验证{'通过' if main_valid else '失败'}")
        
        # 2. 验证 Agent 配置
        print("2. 验证 Agent 配置文件...")
        agent_valid = self.validate_agent_configs()
        print(f"   {'✅' if agent_valid else '❌'} Agent 配置验证{'通过' if agent_valid else '失败'}")
        
        # 3. 验证一致性
        print("3. 验证配置一致性...")
        consistency_valid = self.validate_config_consistency()
        print(f"   {'✅' if consistency_valid else '❌'} 一致性验证{'通过' if consistency_valid else '失败'}")
        
        print()
        
        # 输出详细信息
        if self.info:
            print("📊 信息:")
            for msg in self.info:
                print(f"   - {msg}")
            print()
        
        if self.warnings:
            print("⚠️ 警告:")
            for msg in self.warnings:
                print(f"   - {msg}")
            print()
        
        if self.errors:
            print("❌ 错误:")
            for msg in self.errors:
                print(f"   - {msg}")
            print()
        
        all_valid = main_valid and agent_valid and consistency_valid
        print(f"{'='*50}")
        print(f"验证结果：{'✅ 通过' if all_valid else '❌ 失败'}")
        print(f"错误数：{len(self.errors)}, 警告数：{len(self.warnings)}")
        
        return all_valid


# ==================== 命令行入口 ====================

def main():
    """命令行入口"""
    validator = ConfigValidator()
    success = validator.validate_all()
    
    # 输出验证报告
    report_file = WORKSPACE / 'reports' / f"config_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# 配置验证报告\n\n")
        f.write(f"**验证时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**验证结果**: {'✅ 通过' if success else '❌ 失败'}\n\n")
        
        if validator.info:
            f.write(f"## 信息\n\n")
            for msg in validator.info:
                f.write(f"- {msg}\n")
            f.write("\n")
        
        if validator.warnings:
            f.write(f"## 警告\n\n")
            for msg in validator.warnings:
                f.write(f"- {msg}\n")
            f.write("\n")
        
        if validator.errors:
            f.write(f"## 错误\n\n")
            for msg in validator.errors:
                f.write(f"- {msg}\n")
            f.write("\n")
    
    print(f"\n📄 验证报告已保存：{report_file}")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 配置验证脚本

用途：在修改 openclaw.json 前进行验证测试
使用：python3 verify_config.py [配置文件路径]

原则：先验证，后修改
"""

import json
import sys
import os
from datetime import datetime

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

# 验证 JSON 语法
def verify_json_syntax(file_path):
    """验证 JSON 语法"""
    print_header("1. JSON 语法验证")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print_success("JSON 语法正确")
        return True, config
    except json.JSONDecodeError as e:
        print_error(f"JSON 语法错误：{e}")
        return False, None
    except FileNotFoundError:
        print_error(f"文件不存在：{file_path}")
        return False, None

# 验证必要字段
def verify_required_fields(config):
    """验证必要字段"""
    print_header("2. 必要字段验证")
    
    required_keys = ['agents', 'models', 'tools', 'gateway']
    missing = []
    
    for key in required_keys:
        if key not in config:
            missing.append(key)
            print_error(f"缺少必要字段：{key}")
        else:
            print_success(f"字段存在：{key}")
    
    if missing:
        print_warning(f"缺少 {len(missing)} 个必要字段")
        return False
    else:
        print_success("所有必要字段都存在")
        return True

# 验证 agents 配置
def verify_agents(config):
    """验证 agents 配置"""
    print_header("3. Agents 配置验证")
    
    if 'agents' not in config:
        print_error("agents 配置不存在")
        return False
    
    agents_config = config['agents']
    
    # 验证 defaults
    if 'defaults' not in agents_config:
        print_warning("缺少 agents.defaults，将使用系统默认值")
    else:
        print_success("agents.defaults 存在")
    
    # 验证 list
    if 'list' not in agents_config:
        print_error("缺少 agents.list")
        return False
    
    agents_list = agents_config['list']
    print_info(f"共配置 {len(agents_list)} 个 agents")
    
    # 验证每个 agent
    errors = []
    agent_ids = set()
    
    for i, agent in enumerate(agents_list):
        # 检查 id
        if 'id' not in agent:
            errors.append(f"agents.list[{i}]: 缺少 id 字段")
            continue
        
        agent_id = agent['id']
        
        # 检查重复
        if agent_id in agent_ids:
            errors.append(f"agents.list[{i}]: agent id '{agent_id}' 重复")
        agent_ids.add(agent_id)
        
        # 检查 subagents 配置 (常见错误点)
        if 'subagents' in agent:
            subagents = agent['subagents']
            invalid_keys = []
            valid_keys = ['allowAgents', 'model', 'thinking']
            
            for key in subagents.keys():
                if key not in valid_keys:
                    invalid_keys.append(key)
            
            if invalid_keys:
                errors.append(f"agents.list[{i}].subagents: 无效的字段：{invalid_keys}")
                print_error(f"agent '{agent_id}' 的 subagents 配置错误：{invalid_keys}")
            else:
                print_success(f"agent '{agent_id}' 配置正确")
    
    # 显示错误
    if errors:
        print_header("验证错误")
        for error in errors:
            print_error(error)
        return False
    else:
        print_success("所有 agent 配置都正确")
        return True

# 验证 models 配置
def verify_models(config):
    """验证 models 配置"""
    print_header("4. Models 配置验证")
    
    if 'models' not in config:
        print_warning("缺少 models 配置")
        return True
    
    models_config = config['models']
    
    # 验证 providers
    if 'providers' not in models_config:
        print_warning("缺少 models.providers")
        return True
    
    providers = models_config['providers']
    print_info(f"共配置 {len(providers)} 个 providers")
    
    for provider_name, provider_config in providers.items():
        if 'baseUrl' not in provider_config:
            print_warning(f"provider '{provider_name}' 缺少 baseUrl")
        else:
            print_success(f"provider '{provider_name}' 配置正确")
    
    return True

# 验证 plugins 配置
def verify_plugins(config):
    """验证 plugins 配置"""
    print_header("5. Plugins 配置验证")
    
    if 'plugins' not in config:
        print_info("缺少 plugins 配置 (可选)")
        return True
    
    plugins_config = config['plugins']
    
    # 验证 allow 和 entries 一致性
    if 'allow' in plugins_config and 'entries' in plugins_config:
        allow_set = set(plugins_config['allow'])
        entries_set = set(plugins_config['entries'].keys())
        
        # entries 中的插件必须在 allow 列表中
        not_allowed = entries_set - allow_set
        if not_allowed:
            print_error(f"plugins.entries 中有插件未在 allow 列表中：{not_allowed}")
            print_warning("这会导致插件无法加载")
            return False
        else:
            print_success("plugins.allow 和 entries 一致")
    
    print_info(f"共启用 {len(plugins_config.get('entries', {}))} 个插件")
    return True

# 生成验证报告
def generate_report(results, file_path):
    """生成验证报告"""
    print_header("验证报告")
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    all_passed = all(results.values())
    
    if all_passed:
        print_success("✅ 配置验证通过！")
        print_info(f"配置文件：{file_path}")
        print_info(f"验证时间：{timestamp}")
        print_info("可以安全修改并重启 Gateway")
    else:
        print_error("❌ 配置验证失败！")
        print_info(f"配置文件：{file_path}")
        print_info(f"验证时间：{timestamp}")
        print_warning("请勿修改配置，先修复错误")
        
        failed_checks = [k for k, v in results.items() if not v]
        print_info(f"失败的检查：{', '.join(failed_checks)}")
    
    return all_passed

# 主函数
def main():
    # 配置文件路径
    default_config_path = '/home/uos/.openclaw/openclaw.json'
    
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = default_config_path
    
    print_header("OpenClaw 配置验证工具")
    print_info(f"配置文件：{config_path}")
    print_info(f"验证时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("原则：先验证，后修改")
    
    # 执行验证
    results = {}
    
    # 1. JSON 语法
    success, config = verify_json_syntax(config_path)
    results['JSON 语法'] = success
    if not success:
        generate_report(results, config_path)
        sys.exit(1)
    
    # 2. 必要字段
    success = verify_required_fields(config)
    results['必要字段'] = success
    
    # 3. Agents 配置
    success = verify_agents(config)
    results['Agents 配置'] = success
    
    # 4. Models 配置
    success = verify_models(config)
    results['Models 配置'] = success
    
    # 5. Plugins 配置
    success = verify_plugins(config)
    results['Plugins 配置'] = success
    
    # 生成报告
    all_passed = generate_report(results, config_path)
    
    # 退出码
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()

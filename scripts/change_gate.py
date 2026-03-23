#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置变更门禁脚本

用途：在配置变更前强制执行验证
使用：./change_gate.py check <配置文件>
      ./change_gate.py approve <变更 ID>
      ./change_gate.py deploy <变更 ID>

原则：未通过门禁，禁止变更
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path('/home/uos/.openclaw/workspace')
CHANGES_DIR = WORKSPACE / '.changes'
CHANGES_DIR.mkdir(exist_ok=True)

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

# 创建变更申请
def create_change(description, applicant):
    """创建变更申请"""
    change_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    change_file = CHANGES_DIR / f"{change_id}.json"
    
    change = {
        'id': change_id,
        'description': description,
        'applicant': applicant,
        'created_at': datetime.now().isoformat(),
        'status': 'pending',  # pending, approved, rejected, deployed, completed
        'approvals': [],
        'verifications': [],
        'deployment': None,
        'rollback_plan': None
    }
    
    with open(change_file, 'w', encoding='utf-8') as f:
        json.dump(change, f, indent=2, ensure_ascii=False)
    
    print_success(f"变更申请已创建：{change_id}")
    print_info(f"描述：{description}")
    print_info(f"申请人：{applicant}")
    print_info(f"状态：待审批")
    print_info(f"\n下一步:")
    print_info(f"  1. Rex 审批：./change_gate.py approve {change_id}")
    print_info(f"  2. 验证配置：./change_gate.py verify {change_id}")
    print_info(f"  3. 执行部署：./change_gate.py deploy {change_id}")
    
    return change_id

# 审批变更
def approve_change(change_id, approver, role):
    """审批变更"""
    change_file = CHANGES_DIR / f"{change_id}.json"
    
    if not change_file.exists():
        print_error(f"变更不存在：{change_id}")
        return False
    
    with open(change_file, 'r', encoding='utf-8') as f:
        change = json.load(f)
    
    # 检查审批权限
    if role not in ['CEO', 'Rex']:
        print_error(f"无权审批：{role}")
        return False
    
    change['approvals'].append({
        'approver': approver,
        'role': role,
        'approved_at': datetime.now().isoformat(),
        'comment': '批准变更'
    })
    
    change['status'] = 'approved'
    
    with open(change_file, 'w', encoding='utf-8') as f:
        json.dump(change, f, indent=2, ensure_ascii=False)
    
    print_success(f"变更已批准：{change_id}")
    print_info(f"审批人：{approver} ({role})")
    
    return True

# 验证配置
def verify_change(change_id):
    """验证配置"""
    change_file = CHANGES_DIR / f"{change_id}.json"
    
    if not change_file.exists():
        print_error(f"变更不存在：{change_id}")
        return False
    
    with open(change_file, 'r', encoding='utf-8') as f:
        change = json.load(f)
    
    # 检查是否已审批
    if change['status'] != 'approved':
        print_error(f"变更未审批：{change_id}")
        print_info(f"当前状态：{change['status']}")
        return False
    
    # 运行验证脚本
    print_header("配置验证")
    result = subprocess.run(
        ['python3', str(WORKSPACE / 'scripts' / 'verify_config.py')],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.returncode != 0:
        print_error("配置验证失败")
        change['status'] = 'rejected'
        change['verifications'].append({
            'verified_at': datetime.now().isoformat(),
            'result': 'failed',
            'error': result.stderr
        })
    else:
        print_success("配置验证通过")
        change['verifications'].append({
            'verified_at': datetime.now().isoformat(),
            'result': 'passed'
        })
        change['status'] = 'verified'
    
    with open(change_file, 'w', encoding='utf-8') as f:
        json.dump(change, f, indent=2, ensure_ascii=False)
    
    return result.returncode == 0

# 部署变更
def deploy_change(change_id):
    """部署变更"""
    change_file = CHANGES_DIR / f"{change_id}.json"
    
    if not change_file.exists():
        print_error(f"变更不存在：{change_id}")
        return False
    
    with open(change_file, 'r', encoding='utf-8') as f:
        change = json.load(f)
    
    # 检查是否已验证
    if change['status'] != 'verified':
        print_error(f"变更未验证：{change_id}")
        print_info(f"当前状态：{change['status']}")
        return False
    
    # 备份配置
    print_header("备份配置")
    backup_file = f"/home/uos/.openclaw/openclaw.json.backup.{change_id}"
    subprocess.run(['cp', '/home/uos/.openclaw/openclaw.json', backup_file], check=True)
    print_success(f"配置已备份：{backup_file}")
    
    change['rollback_plan'] = {
        'backup_file': backup_file,
        'rollback_command': f'cp {backup_file} /home/uos/.openclaw/openclaw.json'
    }
    
    # 重启 Gateway
    print_header("重启 Gateway")
    result = subprocess.run(
        ['openclaw', 'gateway', 'restart'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.returncode != 0:
        print_error("Gateway 重启失败")
        print_info("执行回滚...")
        subprocess.run(['cp', backup_file, '/home/uos/.openclaw/openclaw.json'], check=True)
        change['status'] = 'failed'
        change['deployment'] = {
            'deployed_at': datetime.now().isoformat(),
            'result': 'failed',
            'rolled_back': True
        }
    else:
        print_success("Gateway 重启成功")
        change['status'] = 'deployed'
        change['deployment'] = {
            'deployed_at': datetime.now().isoformat(),
            'result': 'success',
            'rolled_back': False
        }
    
    with open(change_file, 'w', encoding='utf-8') as f:
        json.dump(change, f, indent=2, ensure_ascii=False)
    
    return result.returncode == 0

# 完成变更
def complete_change(change_id):
    """完成变更"""
    change_file = CHANGES_DIR / f"{change_id}.json"
    
    if not change_file.exists():
        print_error(f"变更不存在：{change_id}")
        return False
    
    with open(change_file, 'r', encoding='utf-8') as f:
        change = json.load(f)
    
    if change['status'] != 'deployed':
        print_error(f"变更未部署：{change_id}")
        return False
    
    change['status'] = 'completed'
    change['completed_at'] = datetime.now().isoformat()
    
    with open(change_file, 'w', encoding='utf-8') as f:
        json.dump(change, f, indent=2, ensure_ascii=False)
    
    print_success(f"变更已完成：{change_id}")
    
    return True

# 主函数
def main():
    if len(sys.argv) < 2:
        print_header("配置变更门禁系统")
        print_info("用法:")
        print_info("  ./change_gate.py create <描述> <申请人>")
        print_info("  ./change_gate.py approve <变更 ID> <审批人> <角色>")
        print_info("  ./change_gate.py verify <变更 ID>")
        print_info("  ./change_gate.py deploy <变更 ID>")
        print_info("  ./change_gate.py complete <变更 ID>")
        print_info("  ./change_gate.py status <变更 ID>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'create':
        if len(sys.argv) < 4:
            print_error("用法：./change_gate.py create <描述> <申请人>")
            sys.exit(1)
        create_change(sys.argv[2], sys.argv[3])
    
    elif command == 'approve':
        if len(sys.argv) < 5:
            print_error("用法：./change_gate.py approve <变更 ID> <审批人> <角色>")
            sys.exit(1)
        approve_change(sys.argv[2], sys.argv[3], sys.argv[4])
    
    elif command == 'verify':
        if len(sys.argv) < 3:
            print_error("用法：./change_gate.py verify <变更 ID>")
            sys.exit(1)
        verify_change(sys.argv[2])
    
    elif command == 'deploy':
        if len(sys.argv) < 3:
            print_error("用法：./change_gate.py deploy <变更 ID>")
            sys.exit(1)
        deploy_change(sys.argv[2])
    
    elif command == 'complete':
        if len(sys.argv) < 3:
            print_error("用法：./change_gate.py complete <变更 ID>")
            sys.exit(1)
        complete_change(sys.argv[2])
    
    elif command == 'status':
        if len(sys.argv) < 3:
            print_error("用法：./change_gate.py status <变更 ID>")
            sys.exit(1)
        
        change_file = CHANGES_DIR / f"{sys.argv[2]}.json"
        if change_file.exists():
            with open(change_file, 'r', encoding='utf-8') as f:
                change = json.load(f)
            print_header(f"变更状态：{sys.argv[2]}")
            print_info(f"描述：{change['description']}")
            print_info(f"申请人：{change['applicant']}")
            print_info(f"状态：{change['status']}")
            print_info(f"创建时间：{change['created_at']}")
        else:
            print_error(f"变更不存在：{sys.argv[2]}")
    
    else:
        print_error(f"未知命令：{command}")
        sys.exit(1)

if __name__ == '__main__':
    main()

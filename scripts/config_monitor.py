#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置变更监控告警脚本

用途：监控配置变更，发送告警
使用：python3 config_monitor.py

监控项:
- 配置变更频率
- 验证失败次数
- 部署成功率
- 流程执行率
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# 配置
WORKSPACE = Path('/home/uos/.openclaw/workspace')
CHANGES_DIR = WORKSPACE / '.changes'
LOG_FILE = WORKSPACE / 'logs' / 'config_monitor.log'

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log(message, level='INFO'):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    
    # 写入日志文件
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def get_weekly_changes():
    """获取本周变更"""
    if not CHANGES_DIR.exists():
        return []
    
    changes = []
    one_week_ago = datetime.now() - timedelta(days=7)
    
    for change_file in CHANGES_DIR.glob('*.json'):
        with open(change_file, 'r', encoding='utf-8') as f:
            change = json.load(f)
        
        created_at = datetime.fromisoformat(change['created_at'])
        if created_at >= one_week_ago:
            changes.append(change)
    
    return changes

def calculate_compliance_rate(changes):
    """计算流程执行率"""
    if not changes:
        return 100.0
    
    compliant = 0
    for change in changes:
        # 检查是否有完整的流程记录
        has_approvals = len(change.get('approvals', [])) > 0
        has_verifications = len(change.get('verifications', [])) > 0
        has_deployment = change.get('deployment') is not None
        
        if has_approvals and has_verifications and has_deployment:
            compliant += 1
    
    return (compliant / len(changes)) * 100

def check_config_integrity():
    """检查配置完整性"""
    result = subprocess.run(
        ['python3', str(WORKSPACE / 'scripts' / 'verify_config.py')],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def send_alert(message, level='WARNING', recipients=None):
    """发送告警"""
    if recipients is None:
        recipients = ['Rex', 'ClawCoordinator', 'ClawGuard']
    
    alert_message = f"""
🚨 配置变更告警

级别：{level}
时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
内容：{message}

接收人：{', '.join(recipients)}
"""
    
    log(alert_message, level)
    
    # TODO: 集成飞书消息发送
    # subprocess.run(['feishu', 'send', '--to', ','.join(recipients), '--message', alert_message])
    
    print(alert_message)

def generate_monitoring_report():
    """生成监控报告"""
    changes = get_weekly_changes()
    compliance_rate = calculate_compliance_rate(changes)
    config_ok = check_config_integrity()
    
    report = f"""
{'='*60}
配置变更监控周报
{'='*60}

统计周期：过去 7 天
生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【变更统计】
本周变更数：{len(changes)}
成功：{len([c for c in changes if c.get('status') == 'completed'])}
失败：{len([c for c in changes if c.get('status') == 'failed'])}
进行中：{len([c for c in changes if c.get('status') in ['pending', 'approved', 'verified', 'deployed']])}

【流程执行率】
执行率：{compliance_rate:.1f}%
"""
    
    if compliance_rate >= 90:
        report += f"\n{Colors.GREEN}✅ 流程执行率良好{Colors.END}\n"
    elif compliance_rate >= 70:
        report += f"\n{Colors.YELLOW}⚠️  流程执行率需改进{Colors.END}\n"
    else:
        report += f"\n{Colors.RED}❌ 流程执行率不达标{Colors.END}\n"
        send_alert(f"流程执行率仅{compliance_rate:.1f}%，低于 70% 阈值", level='CRITICAL')
    
    report += f"\n【配置完整性】\n"
    if config_ok:
        report += f"{Colors.GREEN}✅ 配置验证通过{Colors.END}\n"
    else:
        report += f"{Colors.RED}❌ 配置验证失败{Colors.END}\n"
        send_alert("配置验证失败，请立即检查", level='CRITICAL')
    
    report += f"""
【变更详情】
"""
    
    for change in changes:
        report += f"""
变更 ID: {change['id']}
描述：{change['description']}
申请人：{change['applicant']}
状态：{change['status']}
创建时间：{change['created_at']}
"""
    
    report += f"\n{'='*60}\n"
    
    return report

def main():
    print(f"\n{Colors.BOLD}配置变更监控系统{Colors.END}\n")
    
    # 生成监控报告
    report = generate_monitoring_report()
    print(report)
    
    # 保存报告
    report_file = WORKSPACE / 'docs' / 'reports' / f"config_monitor_{datetime.now().strftime('%Y%m%d')}.md"
    report_file.parent.mkdir(exist_ok=True)
    
    # 移除颜色代码后保存
    plain_report = report
    for color in [Colors.GREEN, Colors.RED, Colors.YELLOW, Colors.BLUE, Colors.END, Colors.BOLD]:
        plain_report = plain_report.replace(color, '')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(plain_report)
    
    print(f"{Colors.BLUE}ℹ️  报告已保存：{report_file}{Colors.END}\n")

if __name__ == '__main__':
    main()

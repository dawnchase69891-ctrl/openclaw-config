#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cron任务监控脚本
用于监控所有定时任务的健康状况
"""

import subprocess
from datetime import datetime
import json
import logging
from pathlib import Path


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/tmp/cron_monitor.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def check_cron_health():
    """检查所有Cron任务健康状态"""
    logger = setup_logging()
    
    tasks = [
        {
            'name': 'feishu_health_check',
            'expected_interval': 1800,  # 30分钟
            'script': '/home/uos/.openclaw/workspace/scripts/feishu_health_check.py',
            'log_file': '/tmp/feishu_health_check.log'
        },
        {
            'name': 'rebalance_reminder',
            'expected_interval': 28800,  # 8小时（交易时间）
            'script': '/home/uos/.openclaw/workspace/scripts/feishu_rebalance_reminder.py',
            'log_file': '/tmp/rebalance_alerts.log'
        }
    ]
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'tasks': []
    }
    
    for task in tasks:
        try:
            # 检查最后执行时间
            last_run = get_last_run_time(task['log_file'])
            if last_run:
                time_since_run = (datetime.now() - last_run).total_seconds()
                
                # 判断是否超时
                is_healthy = time_since_run < task['expected_interval'] * 2
                
                task_report = {
                    'name': task['name'],
                    'last_run': last_run.isoformat() if last_run else 'N/A',
                    'time_since_run_minutes': int(time_since_run / 60) if last_run else -1,
                    'healthy': is_healthy,
                    'status': 'OK' if is_healthy else 'WARNING'
                }
            else:
                task_report = {
                    'name': task['name'],
                    'last_run': 'N/A',
                    'time_since_run_minutes': -1,
                    'healthy': False,
                    'status': 'MISSING_LOG'
                }
        except Exception as e:
            logger.error("检查任务 %%s 时出错: %%s" %% (task['name'], e))
            task_report = {
                'name': task['name'],
                'last_run': 'ERROR',
                'time_since_run_minutes': -1,
                'healthy': False,
                'status': 'ERROR: %%s' %% str(e)
            }
        
        report['tasks'].append(task_report)
    
    # 保存报告
    report_file = '/tmp/cron_health.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info("Cron健康检查完成，报告已保存到: %%s" %% report_file)
    
    # 打印报告摘要
    print("📋 Cron任务健康检查报告:")
    for task in report['tasks']:
        status_icon = "✅" if task['healthy'] else "❌"
        print("  %%s %%s: %%s" %% (status_icon, task['name'], task['status']))
    
    return report


def get_last_run_time(log_file):
    """从日志文件获取最后执行时间"""
    try:
        log_path = Path(log_file)
        if not log_path.exists():
            return None
            
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                # 解析最后一行的时间戳 [YYYY-MM-DD HH:MM:SS]
                last_line = lines[-1].strip()
                if last_line.startswith('['):
                    timestamp_str = last_line.split(']')[0].strip('[')
                    return datetime.strptime(timestamp_str, '%%Y-%%m-%%d %%H:%%M:%%S')
    except Exception as e:
        print("解析日志时间失败: %%s" %% e)
        return None
    
    return None


if __name__ == '__main__':
    report = check_cron_health()
    print("\n✅ 检查完成，时间: %%s" %% report['timestamp'])

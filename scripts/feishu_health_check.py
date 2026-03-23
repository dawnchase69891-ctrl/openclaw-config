#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书通道健康检查脚本
定期检查飞书 API 连接状态，发现问题自动恢复
"""

import subprocess
import sys
from datetime import datetime
import os

# 配置
LOG_FILE = "/tmp/feishu_health_check.log"
HEARTBEAT_FILE = "/tmp/feishu_heartbeat.json"
MAX_RETRY = 3
CHECK_INTERVAL_MINUTES = 30

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    # 追加到日志文件
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + '\n')

def check_feishu_connection():
    """检查飞书连接状态"""
    log("🔍 开始检查飞书连接...")
    
    try:
        # 执行飞书警报脚本测试连接
        result = subprocess.run(
            ['python3', '/home/uos/.openclaw/workspace/scripts/feishu_alert.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            log("✅ 飞书连接正常")
            write_heartbeat(True, "连接正常")
            return True
        else:
            log(f"❌ 飞书连接异常：{result.stderr}")
            write_heartbeat(False, result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        log("❌ 飞书连接超时")
        write_heartbeat(False, "连接超时")
        return False
    except Exception as e:
        log(f"❌ 检查失败：{str(e)}")
        write_heartbeat(False, str(e))
        return False

def write_heartbeat(status, message):
    """写入心跳文件"""
    import json
    
    heartbeat = {
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy' if status else 'unhealthy',
        'message': message,
        'consecutive_failures': 0 if status else get_consecutive_failures() + 1
    }
    
    with open(HEARTBEAT_FILE, 'w') as f:
        json.dump(heartbeat, f, indent=2)

def get_consecutive_failures():
    """获取连续失败次数"""
    import json
    
    try:
        with open(HEARTBEAT_FILE, 'r') as f:
            data = json.load(f)
            return data.get('consecutive_failures', 0)
    except:
        return 0

def attempt_recovery():
    """尝试恢复飞书连接"""
    log("🔄 尝试恢复飞书连接...")
    
    # 方法 1: 重启 Gateway
    log("  步骤 1: 检查 Gateway 状态...")
    try:
        result = subprocess.run(
            ['openclaw', 'gateway', 'status'],
            capture_output=True,
            text=True,
            timeout=10
        )
        log(f"  Gateway 状态：{result.stdout[:200]}")
    except Exception as e:
        log(f"  无法检查 Gateway: {e}")
    
    # 方法 2: 发送测试消息
    log("  步骤 2: 发送测试消息...")
    test_message = f"""
🏓 飞书通道健康检查

时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
状态：连接测试
类型：自动健康检查

如果收到此消息，说明飞书通道正常。
"""
    
    try:
        # 使用 message 工具发送测试消息
        subprocess.run(
            ['message', 'send', '--target', 'ou_9c111f465a69f41b26e059801d9b79f0', '--message', test_message],
            capture_output=True,
            text=True,
            timeout=30
        )
        log("  ✅ 测试消息已发送")
    except Exception as e:
        log(f"  ❌ 发送测试消息失败：{e}")
    
    return True

def send_alert_notification(failure_count):
    """发送告警通知"""
    alert_message = f"""
⚠️ 飞书通道异常告警

连续失败次数：{failure_count}
检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

建议操作:
1. 检查网络连接
2. 检查飞书 API Token
3. 重启 OpenClaw Gateway: openclaw gateway restart

自动恢复已启动，请稍后检查。
"""
    
    log(f"📱 发送告警通知 (失败{failure_count}次)...")
    
    try:
        subprocess.run(
            ['message', 'send', '--target', 'ou_9c111f465a69f41b26e059801d9b79f0', '--message', alert_message],
            capture_output=True,
            text=True,
            timeout=30
        )
        log("  ✅ 告警通知已发送")
    except Exception as e:
        log(f"  ❌ 发送告警失败：{e}")

def main():
    """主函数"""
    log("=" * 60)
    log("🏓 飞书通道健康检查")
    log("=" * 60)
    
    # 检查连接
    is_healthy = check_feishu_connection()
    
    if not is_healthy:
        failure_count = get_consecutive_failures()
        log(f"⚠️ 连续失败次数：{failure_count}")
        
        # 达到阈值发送告警
        if failure_count >= 3:
            send_alert_notification(failure_count)
        
        # 尝试恢复
        attempt_recovery()
        
        # 再次检查
        log("🔄 恢复后重新检查...")
        is_healthy = check_feishu_connection()
    
    log("=" * 60)
    log(f"✅ 检查完成 - 状态：{'正常' if is_healthy else '异常'}")
    log("=" * 60)
    
    return 0 if is_healthy else 1

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
系统健康自检脚本
检查项目：Gateway 状态、配置文件、飞书通道、Cron 任务、内存使用等
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
OPENCLAW_HOME = Path.home() / ".openclaw"
WORKSPACE = OPENCLAW_HOME / "workspace"
SESSION_STATE = WORKSPACE / "SESSION-STATE.md"
MEMORY_FILE = WORKSPACE / "memory" / f"{datetime.now().strftime('%Y-%m-%d')}.md"

# 检查结果
results = {
    "timestamp": datetime.now().isoformat(),
    "status": "healthy",
    "checks": [],
    "alerts": [],
    "auto_fixes": []
}

def log_check(name, status, message="", auto_fix=None):
    """记录检查结果"""
    check = {
        "name": name,
        "status": status,  # ok, warning, error
        "message": message,
        "auto_fix": auto_fix
    }
    results["checks"].append(check)
    if status in ["warning", "error"]:
        results["alerts"].append(f"{name}: {message}")
    if auto_fix:
        results["auto_fixes"].append(auto_fix)
    print(f"[{status.upper()}] {name}: {message}")

def check_gateway_status():
    """检查 Gateway 状态"""
    try:
        # 检查 Gateway 进程
        result = subprocess.run(
            ["pgrep", "-f", "openclaw"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            log_check("Gateway 状态", "ok", "进程运行中")
        else:
            log_check("Gateway 状态", "error", "Gateway 进程未运行",
                     "运行：openclaw gateway start")
    except Exception as e:
        log_check("Gateway 状态", "warning", f"检查失败：{str(e)}")

def check_config_integrity():
    """检查配置文件完整性"""
    config_path = OPENCLAW_HOME / "openclaw.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # 检查必需配置
        required = ["agents", "channels"]
        missing = [k for k in required if k not in config]
        
        if missing:
            log_check("配置文件", "warning", f"缺少配置项：{missing}")
        else:
            log_check("配置文件", "ok", "配置完整")
            
        # 检查 JSON 语法
        log_check("JSON 语法", "ok", "格式正确")
    except json.JSONDecodeError as e:
        log_check("配置文件", "error", f"JSON 语法错误：{str(e)}", 
                 f"运行：cp {OPENCLAW_HOME}/openclaw.json.backup.* {config_path}")
    except Exception as e:
        log_check("配置文件", "error", f"读取失败：{str(e)}")

def check_feishu_channel():
    """检查飞书通道状态"""
    try:
        # 直接读取配置文件
        config_path = OPENCLAW_HOME / "openclaw.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        feishu_config = config.get("channels", {}).get("feishu", {})
        if feishu_config.get("enabled", True):
            log_check("飞书通道", "ok", "已启用")
        else:
            log_check("飞书通道", "warning", "通道已禁用")
    except Exception as e:
        log_check("飞书通道", "warning", f"检查失败：{str(e)}")

def check_cron_jobs():
    """检查 Cron 任务状态"""
    try:
        # 检查 cron 配置文件
        cron_config = OPENCLAW_HOME / "crons.json"
        if cron_config.exists():
            with open(cron_config, 'r') as f:
                crons = json.load(f)
            cron_count = len(crons.get("jobs", []))
            log_check("Cron 任务", "ok", f"{cron_count} 个任务已配置")
        else:
            log_check("Cron 任务", "warning", "cron 配置文件不存在")
    except Exception as e:
        log_check("Cron 任务", "warning", f"检查失败：{str(e)}")

def check_memory_files():
    """检查记忆文件"""
    try:
        # 检查今日记忆
        if MEMORY_FILE.exists():
            log_check("今日记忆", "ok", f"{MEMORY_FILE.name} 已创建")
        else:
            log_check("今日记忆", "warning", "今日记忆文件未创建",
                     f"运行：touch {MEMORY_FILE}")
        
        # 检查 SESSION-STATE.md
        if SESSION_STATE.exists():
            log_check("SESSION-STATE", "ok", "WAL 协议正常")
        else:
            log_check("SESSION-STATE", "warning", "WAL 文件缺失")
    except Exception as e:
        log_check("记忆文件", "error", f"检查失败：{str(e)}")

def check_disk_usage():
    """检查磁盘使用"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        usage_pct = (used / total) * 100
        
        if usage_pct > 90:
            log_check("磁盘使用", "error", f"使用率 {usage_pct:.1f}% (危险)",
                     "清理临时文件：rm -rf /tmp/openclaw/*")
        elif usage_pct > 80:
            log_check("磁盘使用", "warning", f"使用率 {usage_pct:.1f}% (注意)")
        else:
            log_check("磁盘使用", "ok", f"使用率 {usage_pct:.1f}% (正常)")
    except Exception as e:
        log_check("磁盘使用", "warning", f"检查失败：{str(e)}")

def check_context_usage():
    """检查上下文使用率"""
    try:
        # 检查最近的 session 文件
        session_dir = OPENCLAW_HOME / "agents" / "main" / "sessions"
        if session_dir.exists():
            sessions = list(session_dir.glob("*.jsonl"))
            log_check("上下文使用", "ok", f"{len(sessions)} 个会话文件")
        else:
            log_check("上下文使用", "warning", "会话目录不存在")
    except Exception as e:
        log_check("上下文使用", "warning", f"检查失败：{str(e)}")

def generate_report():
    """生成检查报告"""
    # 更新总体状态
    if any(c["status"] == "error" for c in results["checks"]):
        results["status"] = "critical"
    elif any(c["status"] == "warning" for c in results["checks"]):
        results["status"] = "warning"
    
    # 输出 JSON 报告
    report_path = WORKSPACE / "reports" / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 报告已保存：{report_path}")
    print(f"📈 系统状态：{results['status'].upper()}")
    print(f"✅ 检查项：{len(results['checks'])}")
    print(f"⚠️  警报：{len(results['alerts'])}")
    print(f"🔧 自修复：{len(results['auto_fixes'])}")
    
    return results

def main():
    print("=" * 60)
    print("🔍 OpenClaw 系统健康自检")
    print("=" * 60)
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 执行检查
    check_gateway_status()
    check_config_integrity()
    check_feishu_channel()
    check_cron_jobs()
    check_memory_files()
    check_disk_usage()
    check_context_usage()
    
    # 生成报告
    generate_report()
    
    # 返回状态码
    if results["status"] == "critical":
        sys.exit(2)
    elif results["status"] == "warning":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()

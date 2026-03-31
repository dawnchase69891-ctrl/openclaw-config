#!/bin/bash
# Gateway 确保可用脚本
# 用途：在执行 Cron 任务前确保 Gateway 可用

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="/tmp/openclaw/gateway_ensure.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

main() {
    log "🔍 检查 Gateway 状态..."
    
    # 健康检查
    STATUS=$(bash "$SCRIPT_DIR/gateway_health_check.sh" 2>/dev/null)
    
    if echo "$STATUS" | grep -q "healthy"; then
        log "✅ Gateway 健康，可以执行任务"
        exit 0
    fi
    
    log "⚠️ Gateway 异常，触发自动修复..."
    
    # 自动修复
    FIX_RESULT=$(bash "$SCRIPT_DIR/gateway_auto_fix.sh" 2>/dev/null)
    
    if echo "$FIX_RESULT" | grep -q "fixed"; then
        log "✅ Gateway 修复成功，可以执行任务"
        exit 0
    else
        log "❌ Gateway 修复失败，任务可能失败"
        exit 1
    fi
}

main
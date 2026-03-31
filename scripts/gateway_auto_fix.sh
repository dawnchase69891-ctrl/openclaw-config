#!/bin/bash
# Gateway 自动修复脚本
# 用途：检测异常后自动重启 Gateway

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="/tmp/openclaw/gateway_fix.log"
MAX_RETRIES=3
RETRY_DELAY=5

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "$1"
}

# 停止现有 Gateway
stop_gateway() {
    log "停止现有 Gateway 进程..."
    pkill -f "openclaw gateway" 2>/dev/null || true
    sleep 2
}

# 启动 Gateway
start_gateway() {
    log "启动 Gateway..."
    nohup openclaw gateway > /tmp/openclaw/gateway.log 2>&1 &
    sleep 3
}

# 验证 Gateway 状态
verify_gateway() {
    bash "$SCRIPT_DIR/gateway_health_check.sh" 2>/dev/null
}

# 主修复逻辑
main() {
    log "🔧 开始 Gateway 自动修复..."
    
    for i in $(seq 1 $MAX_RETRIES); do
        log "尝试 $i/$MAX_RETRIES"
        
        stop_gateway
        start_gateway
        
        if verify_gateway | grep -q "healthy"; then
            log "✅ Gateway 修复成功"
            echo "fixed"
            exit 0
        fi
        
        log "修复失败，等待 ${RETRY_DELAY}s 后重试..."
        sleep $RETRY_DELAY
    done
    
    log "❌ Gateway 修复失败，已达最大重试次数"
    echo "failed"
    exit 1
}

main
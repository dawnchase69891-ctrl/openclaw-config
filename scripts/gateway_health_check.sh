#!/bin/bash
# Gateway 健康检查脚本
# 用途：检测 Gateway 是否正常运行

GATEWAY_PORT=18789
GATEWAY_URL="ws://127.0.0.1:$GATEWAY_PORT"
LOG_FILE="/tmp/openclaw/gateway_health.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查端口是否监听
check_port() {
    if netstat -tuln 2>/dev/null | grep -q ":$GATEWAY_PORT "; then
        return 0
    fi
    return 1
}

# 检查 WebSocket 连接
check_websocket() {
    if curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:$GATEWAY_PORT/" 2>/dev/null | grep -q "200\|400"; then
        return 0
    fi
    return 1
}

# 主检查逻辑
main() {
    if check_port && check_websocket; then
        log "✅ Gateway 健康 - 端口 $GATEWAY_PORT 正常"
        echo "healthy"
        exit 0
    else
        log "❌ Gateway 异常 - 需要修复"
        echo "unhealthy"
        exit 1
    fi
}

main
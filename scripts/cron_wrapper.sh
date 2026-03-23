#!/bin/bash
# Cron 任务包装脚本
# 用途：在执行 Cron 任务前确保 Gateway 可用，失败后自动重试

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="/tmp/openclaw/cron_wrapper.log"
MAX_RETRIES=3
RETRY_DELAY=10

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 确保 Gateway 可用
ensure_gateway() {
    bash "$SCRIPT_DIR/gateway_ensure.sh"
    return $?
}

# 执行 Cron 任务
execute_cron_task() {
    local task_name="$1"
    local task_command="$2"
    
    log "📋 开始执行任务: $task_name"
    
    # 检查 Gateway
    if ! ensure_gateway; then
        log "❌ Gateway 不可用，无法执行任务"
        return 1
    fi
    
    # 执行任务
    log "🚀 执行任务命令: $task_command"
    eval "$task_command"
    local result=$?
    
    if [ $result -eq 0 ]; then
        log "✅ 任务执行成功: $task_name"
    else
        log "⚠️ 任务执行失败: $task_name (exit code: $result)"
    fi
    
    return $result
}

# 带重试的任务执行
execute_with_retry() {
    local task_name="$1"
    local task_command="$2"
    
    for i in $(seq 1 $MAX_RETRIES); do
        log "尝试 $i/$MAX_RETRIES: $task_name"
        
        if execute_cron_task "$task_name" "$task_command"; then
            return 0
        fi
        
        if [ $i -lt $MAX_RETRIES ]; then
            log "等待 ${RETRY_DELAY}s 后重试..."
            sleep $RETRY_DELAY
        fi
    done
    
    log "❌ 任务最终失败: $task_name"
    return 1
}

# 主入口
if [ $# -lt 2 ]; then
    echo "用法: $0 <任务名称> <任务命令>"
    echo "示例: $0 'CEO观察者' 'openclaw cron run --name CEO任务检查-观察者'"
    exit 1
fi

TASK_NAME="$1"
TASK_COMMAND="$2"

execute_with_retry "$TASK_NAME" "$TASK_COMMAND"
#!/bin/bash
# Message Queue Management Script for ClawSquad
# 用于管理群消息通知的文件队列系统

MESSAGE_QUEUE_DIR="$HOME/.openclaw/workspace/.message-queue"
INBOX_DIR="$MESSAGE_QUEUE_DIR/inbox"
PROCESSED_DIR="$MESSAGE_QUEUE_DIR/processed"
STATE_FILE="$MESSAGE_QUEUE_DIR/state.json"

# 确保目录存在
mkdir -p "$INBOX_DIR" "$PROCESSED_DIR"

# 功能 1: 写入消息到队列
# 用法：write_message "message_id" "sender" "content" "target_roles"
write_message() {
    local message_id="$1"
    local sender="$2"
    local sender_id="$3"
    local content="$4"
    local chat_id="$5"
    local target_roles="$6"
    local timestamp=$(date -Iseconds)
    
    local filename="$INBOX_DIR/${message_id}.json"
    
    cat > "$filename" << EOF
{
  "message_id": "$message_id",
  "sender": "$sender",
  "sender_id": "$sender_id",
  "timestamp": "$timestamp",
  "content": "$content",
  "chat_id": "$chat_id",
  "target_roles": $target_roles,
  "status": "pending",
  "processed_by": []
}
EOF
    
    echo "Message written: $filename"
}

# 功能 2: 读取未处理消息
# 用法：read_pending_messages [role_name]
read_pending_messages() {
    local role_filter="$1"
    local messages=()
    
    for file in "$INBOX_DIR"/*.json; do
        [ -f "$file" ] || continue
        
        if [ -n "$role_filter" ]; then
            # 检查消息是否包含目标角色
            if grep -q "\"$role_filter\"" "$file"; then
                cat "$file"
                echo "---"
            fi
        else
            cat "$file"
            echo "---"
        fi
    done
}

# 功能 3: 标记消息已处理
# 用法：mark_processed "message_id" "role_name"
mark_processed() {
    local message_id="$1"
    local role_name="$2"
    local filename="$INBOX_DIR/${message_id}.json"
    
    if [ ! -f "$filename" ]; then
        echo "Message not found: $message_id"
        return 1
    fi
    
    # 移动文件到 processed 目录
    mv "$filename" "$PROCESSED_DIR/"
    echo "Message marked as processed: $message_id by $role_name"
}

# 功能 4: 获取待处理消息数量
count_pending() {
    local count=$(ls -1 "$INBOX_DIR"/*.json 2>/dev/null | wc -l)
    echo "$count"
}

# 功能 5: 清理旧消息（超过 7 天）
cleanup_old_messages() {
    local days="${1:-7}"
    find "$PROCESSED_DIR" -name "*.json" -mtime +$days -delete
    echo "Cleaned up messages older than $days days"
}

# 功能 6: 检查是否包含紧急关键词
is_urgent() {
    local content="$1"
    local urgent_keywords=("紧急" "P0" "线上故障" "生产问题" "urgent" "critical")
    
    for keyword in "${urgent_keywords[@]}"; do
        if echo "$content" | grep -qi "$keyword"; then
            echo "true"
            return 0
        fi
    done
    echo "false"
}

# 主程序：根据参数执行不同功能
case "$1" in
    write)
        write_message "$2" "$3" "$4" "$5" "$6" "$7"
        ;;
    read)
        read_pending_messages "$2"
        ;;
    mark)
        mark_processed "$2" "$3"
        ;;
    count)
        count_pending
        ;;
    cleanup)
        cleanup_old_messages "$2"
        ;;
    is_urgent)
        is_urgent "$2"
        ;;
    *)
        echo "Usage: $0 {write|read|mark|count|cleanup|is_urgent} [args...]"
        echo ""
        echo "Commands:"
        echo "  write <msg_id> <sender> <sender_id> <content> <chat_id> <target_roles>"
        echo "  read [role_name]"
        echo "  mark <msg_id> <role_name>"
        echo "  count"
        echo "  cleanup [days]"
        echo "  is_urgent <content>"
        exit 1
        ;;
esac

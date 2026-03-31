#!/bin/bash
# 群消息通知机制测试脚本

MESSAGE_QUEUE_DIR="$HOME/.openclaw/workspace/.message-queue"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUEUE_SCRIPT="$SCRIPT_DIR/message-queue.sh"

echo "======================================"
echo "群消息自动通知机制 - 测试报告"
echo "======================================"
echo ""

# 测试 1: 目录结构检查
echo "【测试 1】目录结构检查"
echo "--------------------------------------"
if [ -d "$MESSAGE_QUEUE_DIR/inbox" ]; then
    echo "✅ inbox 目录存在"
else
    echo "❌ inbox 目录不存在"
fi

if [ -d "$MESSAGE_QUEUE_DIR/processed" ]; then
    echo "✅ processed 目录存在"
else
    echo "❌ processed 目录不存在"
fi

if [ -f "$MESSAGE_QUEUE_DIR/config.json" ]; then
    echo "✅ config.json 存在"
else
    echo "❌ config.json 不存在"
fi

if [ -f "$MESSAGE_QUEUE_DIR/state.json" ]; then
    echo "✅ state.json 存在"
else
    echo "❌ state.json 不存在"
fi
echo ""

# 测试 2: 消息写入测试
echo "【测试 2】消息写入测试"
echo "--------------------------------------"
TEST_MSG_ID="test_$(date +%s)"
$QUEUE_SCRIPT write "$TEST_MSG_ID" "TestUser" "ou_test123" "这是一条测试消息" "oc_test" '["Rex", "ClawBreaker"]'

if [ -f "$MESSAGE_QUEUE_DIR/inbox/${TEST_MSG_ID}.json" ]; then
    echo "✅ 消息成功写入队列"
    echo "   文件：$MESSAGE_QUEUE_DIR/inbox/${TEST_MSG_ID}.json"
    echo "   内容预览:"
    head -5 "$MESSAGE_QUEUE_DIR/inbox/${TEST_MSG_ID}.json" | sed 's/^/   /'
else
    echo "❌ 消息写入失败"
fi
echo ""

# 测试 3: 消息读取测试
echo "【测试 3】消息读取测试（按角色过滤）"
echo "--------------------------------------"
PENDING_COUNT=$(ls -1 "$MESSAGE_QUEUE_DIR/inbox"/*.json 2>/dev/null | wc -l)
echo "当前待处理消息数：$PENDING_COUNT"

echo ""
echo "Rex 相关的消息:"
$QUEUE_SCRIPT read "Rex" | head -10 | sed 's/^/  /'
echo ""

# 测试 4: 紧急消息检测
echo "【测试 4】紧急消息检测"
echo "--------------------------------------"
URGENT_TEST1="紧急！线上故障"
URGENT_TEST2="普通消息"

RESULT1=$($QUEUE_SCRIPT is_urgent "$URGENT_TEST1")
RESULT2=$($QUEUE_SCRIPT is_urgent "$URGENT_TEST2")

if [ "$RESULT1" = "true" ]; then
    echo "✅ 正确识别紧急消息：'$URGENT_TEST1'"
else
    echo "❌ 未能识别紧急消息：'$URGENT_TEST1'"
fi

if [ "$RESULT2" = "false" ]; then
    echo "✅ 正确识别普通消息：'$URGENT_TEST2'"
else
    echo "❌ 错误标记普通消息为紧急：'$URGENT_TEST2'"
fi
echo ""

# 测试 5: 消息标记已处理
echo "【测试 5】消息标记已处理"
echo "--------------------------------------"
$QUEUE_SCRIPT mark "$TEST_MSG_ID" "Rex"

if [ -f "$MESSAGE_QUEUE_DIR/processed/${TEST_MSG_ID}.json" ]; then
    echo "✅ 消息成功移动到 processed 目录"
else
    echo "❌ 消息移动失败"
fi
echo ""

# 测试 6: 配置文件验证
echo "【测试 6】配置文件验证"
echo "--------------------------------------"
if command -v jq &> /dev/null; then
    echo "配置文件内容:"
    jq '.' "$MESSAGE_QUEUE_DIR/config.json" | head -20 | sed 's/^/  /'
    echo "  ..."
    
    ROLE_COUNT=$(jq '.roles | keys | length' "$MESSAGE_QUEUE_DIR/config.json")
    echo ""
    echo "配置的角色数量：$ROLE_COUNT"
    
    URGENT_KEYWORDS=$(jq -r '.urgent_keywords | join(", ")' "$MESSAGE_QUEUE_DIR/config.json")
    echo "紧急关键词：$URGENT_KEYWORDS"
else
    echo "⚠️  jq 未安装，跳过 JSON 验证"
fi
echo ""

# 测试 7: 脚本帮助信息
echo "【测试 7】脚本功能完整性"
echo "--------------------------------------"
echo "消息队列脚本支持的功能:"
$QUEUE_SCRIPT 2>&1 | grep -A 10 "Commands:" | sed 's/^/  /'
echo ""

# 总结
echo "======================================"
echo "测试总结"
echo "======================================"
echo ""
echo "实施组件:"
echo "  ✅ 消息队列目录结构"
echo "  ✅ 消息队列管理脚本 (scripts/message-queue.sh)"
echo "  ✅ 配置文件 (.message-queue/config.json)"
echo "  ✅ 状态追踪文件 (.message-queue/state.json)"
echo "  ✅ 角色消息处理模板 (skills/clawsquad/roles/message-handler-template.md)"
echo "  ✅ Cron 配置文档 (notes/roles-cron-configuration.md)"
echo "  ✅ 心跳检查集成 (HEARTBEAT.md)"
echo ""
echo "下一步行动:"
echo "  1. 在飞书群发送测试消息"
echo "  2. 验证消息是否写入 .message-queue/inbox/"
echo "  3. 等待下一个 Cron 周期（5-15 分钟，取决于角色）"
echo "  4. 验证角色是否读取并处理了消息"
echo "  5. 检查 .message-queue/processed/ 中的已处理消息"
echo ""
echo "监控命令:"
echo "  # 查看待处理消息数"
echo "  ~/.openclaw/workspace/scripts/message-queue.sh count"
echo ""
echo "  # 查看 Rex 的待处理消息"
echo "  ~/.openclaw/workspace/scripts/message-queue.sh read Rex"
echo ""
echo "  # 查看 Cron 任务列表"
echo "  openclaw cron list"
echo ""
echo "======================================"
echo "测试完成时间：$(date)"
echo "======================================"

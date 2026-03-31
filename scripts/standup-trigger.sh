#!/bin/bash
# 站会触发脚本 - 每天 22:00
LOG="/tmp/standup.log"
echo "[$(date)] 站会触发" >> $LOG

# 发送飞书通知 - 提醒站会开始
# 后续会由 ClawCoordinator 在群里主持

echo "[$(date)] 站会触发完成" >> $LOG

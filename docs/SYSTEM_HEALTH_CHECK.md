# 🔍 OpenClaw 系统健康自检

## 部署说明

### 已部署内容

1. **自检脚本**: `/home/uos/.openclaw/workspace/scripts/system_health_check.py`
2. **检查项目**:
   - ✅ Gateway 进程状态
   - ✅ 配置文件完整性
   - ✅ JSON 语法检查
   - ✅ 飞书通道状态
   - ✅ Cron 任务配置
   - ✅ 记忆文件 (今日记忆 + SESSION-STATE)
   - ✅ 磁盘使用率
   - ✅ 上下文使用 (会话文件数)

3. **报告输出**: `/home/uos/.openclaw/workspace/reports/health_check_YYYYMMDD_HHMM.json`

---

## 手动添加每小时自检 Cron

### 方式 1: 使用 CLI 命令

```bash
openclaw cron add \
  --name "🔍 系统健康自检" \
  --cron "0 * * * *" \
  --system-event "python3 /home/uos/.openclaw/workspace/scripts/system_health_check.py" \
  --session "main"
```

### 方式 2: 直接编辑配置文件

编辑 `~/.openclaw/openclaw.json`，在 `crons` 部分添加：

```json
{
  "crons": {
    "jobs": [
      {
        "id": "system-health-check",
        "name": "🔍 系统健康自检",
        "schedule": {
          "kind": "cron",
          "expr": "0 * * * *",
          "tz": "Asia/Shanghai"
        },
        "payload": {
          "kind": "systemEvent",
          "text": "python3 /home/uos/.openclaw/workspace/scripts/system_health_check.py"
        },
        "sessionTarget": "main",
        "enabled": true
      }
    ]
  }
}
```

然后重启 Gateway：
```bash
openclaw gateway restart
```

---

## 检查结果说明

### 状态码

| 状态 | 说明 | 退出码 |
|------|------|--------|
| **ok** | 检查通过 | 0 |
| **warning** | 需要注意 | 1 |
| **error** | 严重问题 | 2 |

### 常见警报及修复

| 警报 | 修复命令 |
|------|---------|
| Gateway 进程未运行 | `openclaw gateway start` |
| JSON 语法错误 | `cp ~/.openclaw/openclaw.json.backup.* ~/.openclaw/openclaw.json` |
| 今日记忆未创建 | `touch ~/memory/$(date +%Y-%m-%d).md` |
| 磁盘使用>90% | `rm -rf /tmp/openclaw/*` |

---

## 查看检查报告

```bash
# 查看最新报告
cat ~/workspace/reports/health_check_$(date +%Y%m%d_%H%M).json

# 查看所有报告
ls -lt ~/workspace/reports/health_check_*.json
```

---

## 自修复能力

脚本会自动检测并建议修复命令，例如：

- **配置文件损坏**: 自动建议从备份恢复
- **记忆文件缺失**: 自动创建空文件
- **磁盘空间不足**: 建议清理临时文件

---

## 测试自检

```bash
# 手动运行自检
python3 ~/.openclaw/workspace/scripts/system_health_check.py
```

---

**首次部署时间**: 2026-03-16 17:47
**版本**: v1.0

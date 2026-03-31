# 🏓 飞书通道健康监控

**创建时间**: 2026-03-09 15:36  
**执行**: 骐骥 (Qíjì) 🐎  
**状态**: ✅ 已激活

---

## 📊 监控配置

### 检查频率

| 类型 | 频率 | 时间 | 说明 |
|------|------|------|------|
| 常规检查 | 每 30 分钟 | 06:00-23:00 | 自动检测连接状态 |
| 早间检查 | 每日 1 次 | 08:00 | 开市前全面检查 |
| 晚间汇总 | 每日 1 次 | 22:00 | 统计当日状态 |

---

## 🔍 检查内容

### 1. 连接测试
- ✅ 执行飞书警报脚本
- ✅ 检测 API 响应
- ✅ 验证 Token 有效性

### 2. 自动恢复
- 🔄 检测到失败自动重试 (最多 3 次)
- 🔄 发送测试消息验证
- 🔄 检查 Gateway 状态

### 3. 告警通知
- ⚠️ 连续失败 3 次 → 发送告警
- ⚠️ 包含恢复建议
- ⚠️ 飞书通知用户

---

## 📁 文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| 监控脚本 | `/home/uos/.openclaw/workspace/scripts/feishu_health_check.py` | 健康检查主脚本 |
| 检查日志 | `/tmp/feishu_health_check.log` | 详细检查日志 |
| 心跳文件 | `/tmp/feishu_heartbeat.json` | 当前状态快照 |
| Cron 配置 | `crontab -l` | 定时任务列表 |

---

## 📈 状态查看

### 实时状态
```bash
cat /tmp/feishu_heartbeat.json
```

### 检查日志
```bash
tail -50 /tmp/feishu_health_check.log
```

### 失败统计
```bash
grep "❌" /tmp/feishu_health_check.log | wc -l
```

---

## ⚠️ 故障处理流程

```
检测到失败
    ↓
记录日志 + 更新心跳
    ↓
连续失败 ≥ 3 次？
    ↓ 是
发送告警通知
    ↓
尝试自动恢复
    ↓
重新检查连接
    ↓
成功？→ 恢复正常
失败？→ 继续告警
```

---

## 🔧 手动操作命令

### 检查当前状态
```bash
python3 ~/.openclaw/workspace/scripts/feishu_health_check.py
```

### 查看心跳
```bash
cat /tmp/feishu_heartbeat.json
```

### 重启 Gateway
```bash
openclaw gateway restart
```

### 测试飞书连接
```bash
python3 ~/.openclaw/workspace/scripts/feishu_alert.py
```

### 查看 Cron 任务
```bash
crontab -l
```

---

## 📊 常见问题排查

### 问题 1: 连续失败
**可能原因**:
- 网络中断
- 飞书 API Token 过期
- Gateway 服务异常

**解决方案**:
1. 检查网络：`ping open.feishu.com`
2. 重启 Gateway: `openclaw gateway restart`
3. 重新配对：`openclaw pairing approve feishu <CODE>`

### 问题 2: 告警未发送
**可能原因**:
- 飞书通道本身故障
- 消息工具配置问题

**解决方案**:
1. 检查 message 工具配置
2. 手动发送测试消息
3. 查看系统日志

### 问题 3: Cron 任务未执行
**可能原因**:
- Cron 服务未启动
- 权限问题

**解决方案**:
```bash
# 检查 Cron 状态
systemctl status cron

# 启动 Cron
sudo systemctl start cron

# 查看 Cron 日志
grep CRON /var/log/syslog | tail -20
```

---

## 📋 监控指标

| 指标 | 目标值 | 告警阈值 |
|------|--------|----------|
| 可用率 | > 99% | < 95% |
| 响应时间 | < 5 秒 | > 30 秒 |
| 连续失败 | 0 次 | ≥ 3 次 |
| 恢复时间 | < 5 分钟 | > 15 分钟 |

---

## ✅ 激活确认

**监控已激活**:
- [x] 健康检查脚本已创建
- [x] Cron 定时任务已配置
- [x] 告警通知已配置
- [x] 自动恢复已启用

**下次检查**: 30 分钟后

---

**创建人**: 骐骥 (Qíjì) 🐎  
**监控开始**: 2026-03-09 15:36  
**首次汇总**: 2026-03-09 22:00

# 调仓提醒系统 v2.0

## 📋 系统概述

动态调仓提醒系统，支持实时价格获取、自动失效机制、计划管理。

### 核心特性

1. ✅ **动态价格获取** - 每次发送提醒前自动获取实时股价
2. ✅ **自动失效机制** - 价格偏离超过10%的建议自动标记过期
3. ✅ **持久化存储** - 调仓建议存储在 JSON 文件，方便每日更新
4. ✅ **执行记录** - 记录每次执行情况，便于复盘
5. ✅ **自动化调度** - 支持 cron 定时任务

---

## 🏗️ 系统架构

```
scripts/
├── feishu_rebalance_reminder.py  # 主脚本（盘前提醒、收盘复盘）
├── init_rebalance_system.py      # 初始化脚本
├── crontab_rebalance             # Cron 定时任务配置
├── lib/
│   ├── price_service.py          # 价格服务（Tushare）
│   └── plan_manager.py           # 计划管理器
└── data/
    ├── rebalance_plans.json      # 调仓计划
    └── rebalance_history.json    # 执行历史
```

---

## 🚀 快速开始

### 1. 初始化系统

```bash
cd /home/uos/.openclaw/workspace/scripts
python3 init_rebalance_system.py
```

### 2. 配置 Tushare Token

```bash
# 设置环境变量
export TUSHARE_TOKEN='your_tushare_token_here'

# 或添加到 ~/.bashrc
echo "export TUSHARE_TOKEN='your_tushare_token_here'" >> ~/.bashrc
source ~/.bashrc
```

### 3. 测试价格获取

```bash
python3 feishu_rebalance_reminder.py refresh
```

### 4. 发送测试提醒

```bash
# 盘前提醒
python3 feishu_rebalance_reminder.py morning

# 收盘复盘
python3 feishu_rebalance_reminder.py evening
```

---

## 📅 定时任务配置

### 手动配置 Cron

```bash
# 编辑 crontab
crontab -e

# 添加以下内容（复制 crontab_rebalance 内容）
0 9 * * 1-5 /usr/bin/python3 /home/uos/.openclaw/workspace/scripts/feishu_rebalance_reminder.py morning >> /home/uos/.openclaw/workspace/logs/rebalance_morning.log 2>&1
30 15 * * 1-5 /usr/bin/python3 /home/uos/.openclaw/workspace/scripts/feishu_rebalance_reminder.py evening >> /home/uos/.openclaw/workspace/logs/rebalance_evening.log 2>&1
0 10-14 * * 1-5 /usr/bin/python3 /home/uos/.openclaw/workspace/scripts/feishu_rebalance_reminder.py refresh >> /home/uos/.openclaw/workspace/logs/rebalance_refresh.log 2>&1

# 创建日志目录
mkdir -p /home/uos/.openclaw/workspace/logs
```

---

## 🔧 命令参考

### 主脚本命令

| 命令 | 说明 | 执行时间 |
|------|------|---------|
| `morning` | 发送盘前提醒（含实时价格） | 09:00 |
| `evening` | 发送收盘复盘 | 15:30 |
| `price` | 发送价格提醒 | 手动触发 |
| `refresh` | 刷新所有计划的价格 | 每小时 |
| `migrate` | 迁移旧数据 | 一次性 |

### 示例

```bash
# 发送盘前提醒
python3 feishu_rebalance_reminder.py morning

# 发送收盘复盘
python3 feishu_rebalance_reminder.py evening

# 刷新价格
python3 feishu_rebalance_reminder.py refresh

# 手动发送价格提醒
python3 feishu_rebalance_reminder.py price 中国卫通 601698 卖出 500 38.50 38.00
```

---

## 📊 数据结构

### 调仓计划 (rebalance_plans.json)

```json
{
  "plans": [
    {
      "id": "plan_20260331120000",
      "stock": "中国卫通",
      "code": "601698",
      "action": "卖出",
      "quantity": 500,
      "target_price": 38.00,
      "current_price": 38.50,
      "priority": "P0",
      "reason": "仓位优化，从 38% 降至 18%",
      "created_date": "2026-03-31",
      "last_updated": "2026-03-31 12:00:00",
      "status": "active",
      "expiry_threshold": 0.10,
      "base_price": 38.00
    }
  ],
  "metadata": {
    "last_refresh": "2026-03-31",
    "version": "1.0"
  }
}
```

### 计划状态

| 状态 | 说明 |
|------|------|
| `active` | 活跃（未过期且未执行） |
| `expired` | 已过期（价格偏离超过阈值） |
| `executed` | 已执行 |

---

## 🔄 工作流程

### 盘前提醒（09:00）

1. 读取调仓计划 → 2. 获取实时价格 → 3. 验证有效性（价格偏离<10%） → 4. 发送提醒

### 盘中监控

1. 定时检查价格 → 2. 对比目标价 → 3. 触发提醒

### 收盘复盘（15:30）

1. 发送复盘 → 2. 记录执行情况 → 3. 更新计划状态

---

## 🛠️ 故障排查

### 问题：价格获取失败

**原因**：未设置 TUSHARE_TOKEN 或 Token 无效

**解决**：
```bash
# 检查环境变量
echo $TUSHARE_TOKEN

# 重新设置
export TUSHARE_TOKEN='your_token'
```

### 问题：cron 任务未执行

**原因**：路径或权限问题

**解决**：
```bash
# 检查 cron 日志
tail -f /home/uos/.openclaw/workspace/logs/rebalance_*.log

# 检查 cron 状态
crontab -l
```

### 问题：计划自动失效

**原因**：价格偏离超过 10%

**解决**：
1. 检查 `data/rebalance_plans.json` 中的 `expiry_reason`
2. 更新 `target_price` 或调整 `expiry_threshold`
3. 手动设置 `status: "active"`

---

## 📝 日常维护

### 添加新计划

编辑 `data/rebalance_plans.json`：

```json
{
  "stock": "新股票",
  "code": "000001",
  "action": "买入",
  "quantity": 1000,
  "target_price": 10.00,
  "priority": "P1",
  "reason": "新机会"
}
```

### 更新目标价

```python
from lib.plan_manager import RebalancePlanManager

manager = RebalancePlanManager()
# 直接编辑 JSON 文件或使用 manager.update_plan_price()
```

### 查看执行历史

```bash
cat /home/uos/.openclaw/workspace/scripts/data/rebalance_history.json
```

---

## 📈 下一步优化

1. **飞书多维表格存储** - 替代本地 JSON，支持多人协作
2. **智能价格提醒** - 基于 Marcus 的市场分析生成调仓建议
3. **Web 界面** - 可视化管理调仓计划
4. **回测分析** - 评估调仓策略的历史表现

---

*Last updated: 2026-03-31*
# Learnings Log

持续学习和改进记录

---

## 使用说明

**记录场景：**
- 用户纠正你（"不对，应该是..."）
- 发现更好的方法
- 知识过时或错误
- 项目特定约定

**格式：**
```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
一句话描述学到的内容

### Details
完整上下文：发生了什么、什么错了、什么是正确的

### Suggested Action
具体的修复或改进建议

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file.ext
- Tags: tag1, tag2
- See Also: LRN-20250110-001 (如果相关)
- Pattern-Key: simplify.dead_code (可选)

---
```

---

## [LRN-20260303-001] self_improvement_install

**Logged**: 2026-03-03T09:36:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
成功安装 self-improving-agent 技能，完成自我改进机制配置

### Details
- 从 ClawHub 安装技能时遇到速率限制 (Rate limit exceeded)
- 等待 30 秒后重试成功
- 技能已安装到 `/home/uos/.openclaw/workspace/skills/self-improving-agent/`
- 钩子已启用：`openclaw hooks enable self-improvement`

### Suggested Action
无需进一步操作，系统已就绪

### Metadata
- Source: conversation
- Related Files: ~/.openclaw/workspace/skills/self-improving-agent/SKILL.md
- Tags: self-improvement, clawhub, installation
- Pattern-Key: clawhub.rate_limit

---

## [LRN-20260303-002] financial_web_update

**Logged**: 2026-03-03T09:42:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: frontend

### Summary
金融 Agent Web 端更新至 v2.0，同步多 Agent 团队功能

### Details
- 原版 Web 端 (v1.0) 缺少 financial_agents.py 的多 Agent 团队展示
- 新增 4 个功能模块：
  1. 多 Agent 团队分析卡片（基本面/情绪/新闻/技术分析师）
  2. 多空辩论展示（多头/空头观点对比）
  3. 风险仪表板（波动率/流动性/风险评分/仓位建议）
  4. 风险警告列表
- 版本号更新为 v2.0，添加版本徽章
- 更新时间戳更新为 2026-03-03 09:40

### Suggested Action
无需进一步操作

### Metadata
- Source: conversation
- Related Files: ~/.openclaw/workspace/agents/financial_agents.py, ~/.openclaw/workspace/stock_dashboard.html
- Tags: finance, web, multi-agent, dashboard
- Pattern-Key: financial.web_sync

---

## [LRN-20260303-003] daily_stock_report

**Logged**: 2026-03-03T10:00:00+08:00
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
完成每日持仓股票分析，生成飞书日报和详细报告

### Details
- 运行时间：10:00 (定时任务)
- 分析股票：6 只持仓股
- 市场情绪：35/100 偏悲观
- 发送飞书警报：6 条
- 生成详细报告：reports/stock_report_2026-03-03.md

**核心建议**:
- 🟢 中国卫通：加仓 (首选)
- 🟡 恒逸石化、汉缆股份、中矿资源：持有
- 🔴 森源电气、广电电气：减仓
- 整体仓位：60% 防守为主

### Metadata
- Source: cron-event
- Related Files: ~/.openclaw/workspace/scripts/feishu_stock_report.py, ~/.openclaw/workspace/reports/stock_report_2026-03-03.md
- Tags: stock, daily-report, feishu
- Pattern-Key: stock.daily_report

---

## [LRN-20260303-004] feishu_daily_report

**Logged**: 2026-03-03T10:03:00+08:00
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
生成并发送 A 股持仓日报到飞书

### Details
- 发送时间：10:03
- 市场情绪：35/100 偏悲观
- 大盘指数：上证 -0.86%, 深证 -1.51%, 创业板 -0.59%
- 飞书消息：已发送
- 报告文件：reports/stock_report_2026-03-03.md

### Metadata
- Source: cron-event
- Related Files: ~/.openclaw/workspace/scripts/feishu_stock_report.py
- Tags: stock, feishu, daily-report
- Pattern-Key: stock.feishu_report

---

## [LRN-20260303-004] daily_record_db

**Logged**: 2026-03-03T10:04:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: backend

### Summary
运行 daily_record.py 脚本，将今日交易建议保存到 stock_database.db

### Details
- 执行时间：10:04
- 获取股票数据：6 只
- 生成交易建议：6 条
- 保存状态：✅ 成功

**建议记录**:
- 000703 恒逸石化：🟡 持有/部分止盈
- 002358 森源电气：🔴 减仓/止损
- 002498 汉缆股份：🟡 持有
- 002738 中矿资源：🟡 持有
- 601616 广电电气：🔴 减仓/观望
- 601698 中国卫通：🟡 持有

### Metadata
- Source: cron-event
- Related Files: ~/.openclaw/workspace/scripts/daily_record.py, ~/.openclaw/workspace/stock_database.db
- Tags: stock, database, daily-record
- Pattern-Key: stock.db_record

---

## [LRN-20260303-005] ui_designer_agent

**Logged**: 2026-03-03T10:05:00+08:00
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
创建 UI/UX Designer Agent，加入产研 Agent 团队

### Details
**背景**: 用户反馈 Web UI 感觉一般，需要专业 UI 设计角色

**新增 Agent**:
- 文件：`agents/ui_designer_agent.py` (15KB)
- 核心功能:
  - UI 评审 (视觉/体验/一致性/可访问性 4 维度)
  - UI 原型生成
  - 设计系统维护
  - 设计任务管理

**设计原则**:
- 简洁优先、一致性、用户中心
- 可访问性、性能友好、情感化

**设计系统 Token**:
- 主色：#667eea
- 辅助色：#764ba2
- 成功/警告/危险色：#4caf50/#ff9800/#f44336

**测试评分**: 股票看板 UI 评审 77.5/100
- 视觉设计：85
- 用户体验：70 (需优化)
- 一致性：85
- 可访问性：70 (需优化)

**文档更新**:
- `agents/PROD_TEAM.md` - 产研团队 v2.0 文档

### Suggested Action
后续可用 UI Designer Agent 优化现有 Web 看板 UI

### Metadata
- Source: user_feedback
- Related Files: ~/.openclaw/workspace/agents/ui_designer_agent.py, ~/.openclaw/workspace/agents/PROD_TEAM.md
- Tags: ui, agent, product-team, design-system
- Pattern-Key: product_team.ui_role

---

## [LRN-20260303-006] scheduled_tasks_10am

**Logged**: 2026-03-03T10:11:00+08:00
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
执行 10:00 定时任务组，记录交易建议并发送警报

### Details
**执行脚本**:
1. `daily_record_v2.py` - 多数据源交易建议记录
2. `event_tracker.py` - 事件追踪与智能警报
3. `feishu_alert.py` - 飞书警报推送

**执行结果**:
- ✅ daily_record_v2.py: 获取 6 只股票数据，保存 6 条建议
- ✅ event_tracker.py: 触发 2 条警报 (中国卫通股价异动/主力流入)
- ✅ feishu_alert.py: 发送 2 条飞书警报

**今日交易建议**:
| 股票 | 建议 | 仓位 |
|------|------|------|
| 中国卫通 | 🟡 持有 | 60% |
| 恒逸石化 | 🟡 持有/部分止盈 | 50% |
| 中矿资源 | 🟡 持有 | 60% |
| 森源电气 | 🔴 减仓/止损 | 30% |
| 广电电气 | 🔴 减仓/观望 | 30% |
| 汉缆股份 | 🟡 持有 | 70% |

**生成报告**: `reports/structured_report_2026-03-03.md`

### Metadata
- Source: cron-event
- Related Files: ~/.openclaw/workspace/scripts/daily_record_v2.py, event_tracker.py, feishu_alert.py
- Tags: stock, cron, alerts, feishu
- Pattern-Key: stock.cron_tasks

---

## [LRN-20260303-007] event_tracker_1015

**Logged**: 2026-03-03T10:15:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: backend

### Summary
执行事件追踪脚本，检查价格和情绪警报

### Details
**执行时间**: 10:15

**检测结果**:
- 价格警报：2 条触发
  - 🔴 中国卫通 (601698): 股价异动 (涨跌幅超过 5%)
  - 🟡 中国卫通 (601698): 主力大幅流入 (超过 5000 万)
- 市场情绪：正常
- 即将事件：无

**后续**: 警报将由 feishu_alert.py 推送

### Metadata
- Source: cron-event
- Related Files: ~/.openclaw/workspace/scripts/event_tracker.py
- Tags: stock, alerts, event-tracker
- Pattern-Key: stock.event_check

---

## [LRN-20260303-008] web_ui_optimization

**Logged**: 2026-03-03T10:26:00+08:00
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
优化金融 Agent Web UI，添加自选股模块

### Details
**UI/UX Designer 评审结果**: 77.5/100
- 视觉设计：90 ✅
- 用户体验：70 ⚠️
- 一致性：80 ✅
- 可访问性：70 ⚠️

**优化内容**:

1. **视觉设计提升**:
   - 卡片悬停动效 (translateY + shadow)
   - 渐变背景优化
   - 圆角统一 (12px-20px)
   - 阴影层次增强
   - 动画效果 (fadeInUp)

2. **新增自选股模块**:
   - 4 只关注股票 (科创新源、中来股份、冰轮环境、华如科技)
   - 蓝色主题区分持仓股
   - 显示关注理由标签
   - 评分和观望状态徽章

3. **交互优化**:
   - 卡片悬停反馈
   - 表格行悬停效果
   - 按钮悬停动效
   - 板块趋势项滑动效果

4. **响应式改进**:
   - 移动端自适应
   - 断点优化 (640px, 1024px)

**文件更新**:
- `config.json` - 添加 watchlist 配置
- `financial_agents.py` - 添加 analyze_watchlist_stock() 函数
- `stock_dashboard.html` - 全面优化 (38KB)

### Metadata
- Source: user_request
- Related Files: ~/.openclaw/workspace/stock_dashboard.html, config.json, financial_agents.py
- Tags: ui, optimization, watchlist, web
- Pattern-Key: finance.web_ui_enhancement

---

## [LRN-20260303-009] event_tracker_1045

**Logged**: 2026-03-03T10:45:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: backend

### Summary
执行事件追踪脚本，检查价格和情绪警报

### Details
**执行时间**: 10:45

**检测结果**:
- 价格警报：2 条触发
  - 🔴 中国卫通 (601698): 股价异动 (涨跌幅超过 5%)
  - 🟡 中国卫通 (601698): 主力大幅流入 (超过 5000 万)
- 市场情绪：正常
- 即将事件：无

**后续**: 警报将由 feishu_alert.py 推送

### Metadata
- Source: cron-event
- Related Files: ~/.openclaw/workspace/scripts/event_tracker.py
- Tags: stock, alerts, event-tracker
- Pattern-Key: stock.event_check

---

## [LRN-20260303-010] emoji_compatibility_fix

**Logged**: 2026-03-03T10:47:00+08:00
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
修复 Web 页面 emoji 乱码问题，创建 QA 测试清单

### Details
**问题**: 持仓股票的状态徽章 (🟡🔴🟢) 在某些系统/浏览器上显示为乱码

**修复方案**:
1. 添加 emoji 字体支持到 body font-family
2. 创建 CSS 圆点类 (`.status-dot`) 替代 emoji
3. 替换所有关键位置的 emoji 为 CSS+ 文字方案

**修改位置**:
- 持仓股票表格：🟡→黄色圆点 + "持有"
- 交易建议按钮：🟢→绿色圆点 + "加仓"
- 自选股徽章：🟡→黄色圆点 + "观望"
- 多 Agent 卡片：🟢→绿色圆点

**新增文件**:
- `QA_CHECKLIST.md` - 测试检查清单
  - UI/UX 专项测试
  - 浏览器兼容性测试
  - 设备兼容性测试
  - Bug 报告模板
  - 发布检查清单

### Suggested Action
后续发布前需按 QA_CHECKLIST.md 执行测试

### Metadata
- Source: user_feedback
- Related Files: ~/.openclaw/workspace/stock_dashboard.html, QA_CHECKLIST.md
- Tags: bugfix, emoji, compatibility, qa, testing
- Pattern-Key: web.emoji_compatibility

---

## [LRN-20260303-011] event_tracker_1100

**Logged**: 2026-03-03T11:00:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: backend

### Summary
执行事件追踪脚本，检查价格和情绪警报

### Details
**执行时间**: 11:00

**检测结果**:
- 价格警报：2 条触发
  - 🔴 中国卫通 (601698): 股价异动 (涨跌幅超过 5%)
  - 🟡 中国卫通 (601698): 主力大幅流入 (超过 5000 万)
- 市场情绪：正常
- 即将事件：无

**后续**: 警报将由 feishu_alert.py 推送

### Metadata
- Source: cron-event
- Related Files: ~/.openclaw/workspace/scripts/event_tracker.py
- Tags: stock, alerts, event-tracker
- Pattern-Key: stock.event_check

---

## [LRN-20260303-012] remove_002358

**Logged**: 2026-03-03T11:05:00+08:00
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
森源电气 (002358) 已清仓，从持仓股中移除

### Details
**操作**:
- 从 `config.json` 移除森源电气配置
- 从 `stock_dashboard.html` 移除持仓表格行
- 从 `stock_dashboard.html` 移除交易建议行

**持仓变化**:
- 移除前：6 只股票
- 移除后：5 只股票

**当前持仓**:
| 代码 | 名称 | 状态 |
|------|------|------|
| 000703 | 恒逸石化 | 持有 |
| 002498 | 汉缆股份 | 持有 |
| 002738 | 中矿资源 | 持有 |
| 601616 | 广电电气 | 减仓 |
| 601698 | 中国卫通 | 加仓 |

### Metadata
- Source: user_request
- Related Files: ~/.openclaw/workspace/config.json, stock_dashboard.html
- Tags: portfolio, stock, remove
- Pattern-Key: portfolio.stock_removal

---

## [LRN-20260303-013] web_stock_management

**Logged**: 2026-03-03T11:10:00+08:00
**Priority**: high
**Status**: resolved
**Area**: frontend

### Summary
为 Web 页面添加股票添加/删除功能

### Details
**用户需求**: 在 Web 页面上对持仓股和关注股添加添加和删除能力

**实现内容**:

1. **前端 UI**:
   - 添加股票按钮 (持仓股/自选股卡片头部)
   - 删除按钮 (每只股票操作列)
   - 添加股票模态框 (支持输入代码/名称/成本或理由)
   - 删除确认模态框
   - Toast 提示框

2. **后端 API** (`scripts/stocks_api.py`):
   - `GET /api/stocks/list` - 获取股票列表
   - `POST /api/stocks/add` - 添加股票
   - `POST /api/stocks/delete` - 删除股票
   - 自动记录操作到 learnings

3. **交互流程**:
   - 点击"添加"→ 弹出模态框 → 填写信息 → 确认 → 刷新页面
   - 点击"删除"→ 弹出确认 → 确认 → 刷新页面

**启动 API 服务**:
```bash
python3 ~/.openclaw/workspace/scripts/stocks_api.py 8080
```

**文件更新**:
- `stock_dashboard.html` - 添加 UI 和 JavaScript (v2.2)
- `scripts/stocks_api.py` - 新建 API 服务

### Metadata
- Source: user_request
- Related Files: ~/.openclaw/workspace/stock_dashboard.html, scripts/stocks_api.py
- Tags: web, ui, stocks, management, api
- Pattern-Key: web.stock_management

---

## [LRN-20260303-014] event_tracker_1115

**Logged**: 2026-03-03T11:15:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: backend

### Summary
执行事件追踪脚本，检查价格和情绪警报

### Details
**执行时间**: 11:15

**检测结果**:
- 价格警报：2 条触发
  - 🔴 中国卫通 (601698): 股价异动 (涨跌幅超过 5%)
  - 🟡 中国卫通 (601698): 主力大幅流入 (超过 5000 万)
- 市场情绪：正常
- 即将事件：无

**后续**: 警报将由 feishu_alert.py 推送

### Metadata
- Source: cron-event
- Related Files: ~/.openclaw/workspace/scripts/event_tracker.py
- Tags: stock, alerts, event-tracker
- Pattern-Key: stock.event_check

---

## [LRN-20260303-ADD600000] portfolio_stock_added

**Logged**: 2026-03-03T11:29:14+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加持仓股: 600000 测试银行

### Details
- 操作类型：添加
- 股票列表：持仓股
- 股票代码：600000
- 股票名称：测试银行

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-DEL600000] portfolio_stock_removed

**Logged**: 2026-03-03T11:29:14+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
删除持仓股: 600000 测试银行

### Details
- 操作类型：删除
- 股票列表：持仓股
- 股票代码：600000
- 股票名称：测试银行

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, delete
- Pattern-Key: portfolio.stock_delete

---

## [LRN-20260303-ADD600001] portfolio_stock_added

**Logged**: 2026-03-03T11:29:14+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加自选股: 600001 测试科技

### Details
- 操作类型：添加
- 股票列表：自选股
- 股票代码：600001
- 股票名称：测试科技

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-DEL600001] portfolio_stock_removed

**Logged**: 2026-03-03T11:29:14+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
删除自选股: 600001 测试科技

### Details
- 操作类型：删除
- 股票列表：自选股
- 股票代码：600001
- 股票名称：测试科技

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, delete
- Pattern-Key: portfolio.stock_delete

---

## [LRN-20260303-ADD600000] portfolio_stock_added

**Logged**: 2026-03-03T11:29:14+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加自选股: 600000 测试

### Details
- 操作类型：添加
- 股票列表：自选股
- 股票代码：600000
- 股票名称：测试

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-ADD600000] portfolio_stock_added

**Logged**: 2026-03-03T11:34:02+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加持仓股: 600000 测试银行

### Details
- 操作类型：添加
- 股票列表：持仓股
- 股票代码：600000
- 股票名称：测试银行

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-DEL600000] portfolio_stock_removed

**Logged**: 2026-03-03T11:34:02+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
删除持仓股: 600000 测试银行

### Details
- 操作类型：删除
- 股票列表：持仓股
- 股票代码：600000
- 股票名称：测试银行

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, delete
- Pattern-Key: portfolio.stock_delete

---

## [LRN-20260303-ADD600001] portfolio_stock_added

**Logged**: 2026-03-03T11:34:02+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加自选股: 600001 测试科技

### Details
- 操作类型：添加
- 股票列表：自选股
- 股票代码：600001
- 股票名称：测试科技

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-DEL600001] portfolio_stock_removed

**Logged**: 2026-03-03T11:34:02+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
删除自选股: 600001 测试科技

### Details
- 操作类型：删除
- 股票列表：自选股
- 股票代码：600001
- 股票名称：测试科技

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, delete
- Pattern-Key: portfolio.stock_delete

---

## [LRN-20260303-ADD600000] portfolio_stock_added

**Logged**: 2026-03-03T11:34:02+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加自选股: 600000 测试

### Details
- 操作类型：添加
- 股票列表：自选股
- 股票代码：600000
- 股票名称：测试

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-ADD600000] portfolio_stock_added

**Logged**: 2026-03-03T11:34:15+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加持仓股: 600000 测试银行

### Details
- 操作类型：添加
- 股票列表：持仓股
- 股票代码：600000
- 股票名称：测试银行

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-DEL600000] portfolio_stock_removed

**Logged**: 2026-03-03T11:34:15+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
删除持仓股: 600000 测试银行

### Details
- 操作类型：删除
- 股票列表：持仓股
- 股票代码：600000
- 股票名称：测试银行

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, delete
- Pattern-Key: portfolio.stock_delete

---

## [LRN-20260303-ADD600001] portfolio_stock_added

**Logged**: 2026-03-03T11:34:15+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加自选股: 600001 测试科技

### Details
- 操作类型：添加
- 股票列表：自选股
- 股票代码：600001
- 股票名称：测试科技

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-DEL600001] portfolio_stock_removed

**Logged**: 2026-03-03T11:34:15+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
删除自选股: 600001 测试科技

### Details
- 操作类型：删除
- 股票列表：自选股
- 股票代码：600001
- 股票名称：测试科技

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, delete
- Pattern-Key: portfolio.stock_delete

---

## [LRN-20260303-ADD600000] portfolio_stock_added

**Logged**: 2026-03-03T11:34:15+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加自选股: 600000 测试

### Details
- 操作类型：添加
- 股票列表：自选股
- 股票代码：600000
- 股票名称：测试

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-ADD600000] portfolio_stock_added

**Logged**: 2026-03-03T11:34:26+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加自选股: 600000 测试

### Details
- 操作类型：添加
- 股票列表：自选股
- 股票代码：600000
- 股票名称：测试

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-ADD600000] portfolio_stock_added

**Logged**: 2026-03-03T12:21:16+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加持仓股: 600000 测试银行

### Details
- 操作类型：添加
- 股票列表：持仓股
- 股票代码：600000
- 股票名称：测试银行

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-DEL600000] portfolio_stock_removed

**Logged**: 2026-03-03T12:21:16+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
删除持仓股: 600000 测试银行

### Details
- 操作类型：删除
- 股票列表：持仓股
- 股票代码：600000
- 股票名称：测试银行

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, delete
- Pattern-Key: portfolio.stock_delete

---

## [LRN-20260303-ADD600001] portfolio_stock_added

**Logged**: 2026-03-03T12:21:16+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加自选股: 600001 测试科技

### Details
- 操作类型：添加
- 股票列表：自选股
- 股票代码：600001
- 股票名称：测试科技

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-DEL600001] portfolio_stock_removed

**Logged**: 2026-03-03T12:21:16+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
删除自选股: 600001 测试科技

### Details
- 操作类型：删除
- 股票列表：自选股
- 股票代码：600001
- 股票名称：测试科技

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, delete
- Pattern-Key: portfolio.stock_delete

---

## [LRN-20260303-ADD600000] portfolio_stock_added

**Logged**: 2026-03-03T12:21:16+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加自选股: 600000 测试

### Details
- 操作类型：添加
- 股票列表：自选股
- 股票代码：600000
- 股票名称：测试

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-ADD600000] portfolio_stock_added

**Logged**: 2026-03-03T12:21:43+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加持仓股: 600000 测试银行

### Details
- 操作类型：添加
- 股票列表：持仓股
- 股票代码：600000
- 股票名称：测试银行

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-DEL600000] portfolio_stock_removed

**Logged**: 2026-03-03T12:21:43+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
删除持仓股: 600000 测试银行

### Details
- 操作类型：删除
- 股票列表：持仓股
- 股票代码：600000
- 股票名称：测试银行

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, delete
- Pattern-Key: portfolio.stock_delete

---

## [LRN-20260303-ADD600001] portfolio_stock_added

**Logged**: 2026-03-03T12:21:43+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
添加自选股: 600001 测试科技

### Details
- 操作类型：添加
- 股票列表：自选股
- 股票代码：600001
- 股票名称：测试科技

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, add
- Pattern-Key: portfolio.stock_add

---

## [LRN-20260303-DEL600001] portfolio_stock_removed

**Logged**: 2026-03-03T12:21:43+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
删除自选股: 600001 测试科技

### Details
- 操作类型：删除
- 股票列表：自选股
- 股票代码：600001
- 股票名称：测试科技

### Metadata
- Source: web_ui_action
- Related Files: ~/.openclaw/workspace/config.json
- Tags: portfolio, stock, delete
- Pattern-Key: portfolio.stock_delete

---

## 2026-03-13 - 子 Agent 分配机制缺失

**问题**：一直是骐骥在执行所有任务，没有分配给专业子 Agent（Rex/ClawOps/ClawBuilder 等）

**根因**：
1. 子 Agent 列表为空（agents_list 只显示 main）
2. ClawSquad 只是技能文档，没有实际激活
3. 骐骥缺乏" delegator"思维，习惯亲力亲为
4. 没有任务路由机制

**改进措施**：
1. 配置子 Agent 允许列表
2. 实现任务类型 → 子 Agent 路由逻辑
3. 骐骥角色定位：CEO（战略/分配）而不是执行者
4. 遇到部署/运维任务 → spawn ClawOps
5. 遇到架构设计 → spawn Rex/ClawBreaker
6. 遇到编码实现 → spawn ClawBuilder

**触发条件**：
- 用户提到"专业人做专业事"
- 任务遇到权限/系统级问题
- 需要并行处理多个任务

---


## 2026-03-13 - OpenClaw 插件配置一致性错误

### ❌ 错误描述

配置 OpenClaw 插件时，在 `plugins.entries` 中启用了插件，但忘记在 `plugins.allow` 列表中添加该插件，导致网关启动失败。

### 🔍 错误配置示例

```json
{
  "plugins": {
    "allow": [
      "openclaw-lark",
      "qwen-portal-auth"
      // ❌ 缺少 "skillhub"
    ],
    "entries": {
      "skillhub": {
        "enabled": true,  // ← 启用了但不在 allow 列表
        "config": { ... }
      }
    }
  }
}
```

### 🚨 错误症状

- 网关启动失败
- 日志报错：`plugin disabled (not in allowlist) but config is present`
- 配置验证失败

### ✅ 正确配置

```json
{
  "plugins": {
    "allow": [
      "openclaw-lark",
      "qwen-portal-auth",
      "skillhub"  // ← 必须在 allow 列表中
    ],
    "entries": {
      "skillhub": {
        "enabled": true,
        "config": { ... }
      }
    }
  }
}
```

### 📋 配置规则

**OpenClaw 插件配置必须满足**：
1. `plugins.allow` 列表包含所有允许使用的插件
2. `plugins.entries` 中配置的插件必须在 `allow` 列表中
3. 如果 `entries` 中 `enabled: true` 但不在 `allow` 中 → 网关启动失败

### 🛠️ 修复步骤

```bash
# 1. 编辑配置文件
cd ~/.openclaw
python3 << 'PYTHON'
import json
with open('openclaw.json', 'r') as f:
    config = json.load(f)

# 添加缺失的插件到 allow 列表
if 'skillhub' not in config['plugins']['allow']:
    config['plugins']['allow'].append('skillhub')

with open('openclaw.json', 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
print("✅ 配置已修复")
PYTHON

# 2. 重启网关
systemctl --user restart openclaw-gateway

# 3. 验证状态
systemctl --user status openclaw-gateway
```

### 🎯 教训总结

1. **配置一致性检查**：修改 `entries` 时必须同步检查 `allow` 列表
2. **自动化验证**：应该添加配置验证脚本
3. **文档化**：在 TOOLS.md 中记录这个配置规则

### 📝 待办

- [ ] 在 TOOLS.md 中添加插件配置规则说明
- [ ] 创建配置验证脚本（可选）
- [ ] 配置修改时的检查清单

---

## [LRN-20260313-001] openclaw_agents_list_no_allow_all

**Logged**: 2026-03-13T18:28:00+08:00
**Priority**: high
**Status**: pending
**Area**: config

### Summary
OpenClaw 的 `agents.list` 里定义了就是可用，不需要额外的 `"allow_all": true` 开关。之前错误地删除了这一行导致问题。

### Details

**错误操作**：
修改配置时，直接删除了 `"allow_all": true` 这一行（以及前面的逗号），认为不需要这个开关。

**正确理解**：
- OpenClaw 使用 `agents.list` 来定义可用的 Agent
- 只要在 `agents.list` 中定义了，就是可用的
- 不需要额外的 `"allow_all": true` 开关来控制
- 配置应该保持简洁，不要画蛇添足

**正确做法**：
1. 检查 `agents.list` 确认 Agent 已定义
2. 不要随意删除配置项，除非明确知道其作用
3. 修改配置前先查文档或询问用户

### Impact

- 可能导致 Agent 无法正常使用
- 配置混乱，增加调试难度
- 用户需要额外时间纠正错误

### Suggested Action

1. ✅ **立即执行**：在 TOOLS.md 中记录此规则
2. ✅ **立即执行**：修改任何配置前先确认作用
3. 📋 **建议**：创建配置修改检查清单

### Metadata

- **Source**: user_feedback
- **Related Files**: `~/.openclaw/openclaw.json`, `~/.openclaw/agents/main/agents.list`
- **Tags**: config, agents, openclaw, allow_all
- **Pattern-Key**: `openclaw.agents_list_no_allow_all`
- **Learned From**: Jason (用户纠正)

### Rule (记住！)

> **OpenClaw Agent 配置规则**：
> - ✅ `agents.list` 里定义了 = 可用
> - ❌ 不需要 `"allow_all": true` 开关
> - ❌ 不要随意删除配置项

---


## 2026-03-13 - OpenClaw 子 Agent 配置错误

### ❌ 错误配置

在 `openclaw.json` 中添加了无效的配置项：

```json
{
  "agents": {
    "allowAny": true  // ❌ 错误：Unrecognized key
  }
}
```

### 🚨 错误症状

- Gateway 启动报错：`agents: Unrecognized key: "allowAny"`
- 子 Agent spawn 失败：`agentId is not allowed for sessions_spawn (allowed: none)`

### ✅ 正确理解

OpenClaw 的子 Agent 配置不需要 `allowAny` 开关：
- `agents.list` 中定义了就是可用
- 不需要额外的 `"allowAll": true` 开关
- 不要随意添加配置项，除非明确知道其作用

### 📝 教训

1. 修改配置前先查文档或问用户
2. 不要猜测配置项的作用
3. 修改后要测试验证
4. 记录到 LEARNINGS.md

### 🔧 正确的子 Agent spawn 方式

需要进一步研究 OpenClaw 文档或询问用户正确的配置方式。

---


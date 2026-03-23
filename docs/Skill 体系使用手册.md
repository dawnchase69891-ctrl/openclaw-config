# 📚 ClawSquad Skill 体系使用手册

**版本**: v1.0  
**整理日期**: 2026-03-16  
**维护者**: ClawCoordinator + Rex  
**状态**: ✅ 已整理

---

## 📊 Skill 总览

### 数量统计

| 类别 | 数量 | 位置 |
|------|------|------|
| **Workspace Skill** | 43 个 | `/home/uos/.openclaw/workspace/skills/` |
| **Feishu Skill** | 9 个 | `/home/uos/.openclaw/extensions/openclaw-lark/skills/` |
| **总计** | 52 个 | - |

### 分类统计

| 类别 | Skill 数量 | 代表 Skill |
|------|-----------|-----------|
| 金融投资 | 15 | a-stock-monitor, finnhub-pro, backtest-expert |
| 飞书集成 | 9 | feishu-bitable, feishu-calendar, feishu-task |
| 数据分析 | 5 | data-analysis, dashboard, financial-calculator |
| 市场研究 | 3 | market-analysis-cn, market-environment-analysis |
| 工具效率 | 10 | find-skills, gog, agent-browser |
| 角色技能 | 10 | clawsquad, clawmarketer, clawcoordinator |

---

## 📋 Skill 详细清单

### 一、金融投资类 (15 个)

#### 1. a-stock-monitor ⭐⭐⭐⭐⭐

**用途**: A 股量化监控系统

**使用场景**:
- 每日 A 股市场分析
- 股票推荐 (短线/中长线)
- 市场情绪评分
- 实时价格监控

**触发词**:
- "A 股分析"
- "股票推荐"
- "市场情绪"
- "量化监控"

**调用方式**:
```python
# 自动触发 (Cron)
每日 10:00 → a-stock-monitor → 生成日报

# 手动触发
@ClawBreaker 分析今天 A 股市场
```

**协同 Skill**:
- finnhub-pro (美股数据)
- tushare-finance (数据采集)
- dashboard (数据展示)

---

#### 2. finnhub-pro ⭐⭐⭐⭐

**用途**: 美股/全球股票数据

**使用场景**:
- 查股价
- 查公司信息
- 看最新新闻
- 内部人交易
- 财报日期

**触发词**:
- "查股价"
- "NVDA 怎么样"
- "财报日期"
- "内部人交易"

**调用方式**:
```bash
@ClawHunter 查一下 NVDA 的最新股价和财报日期
```

**协同 Skill**:
- a-stock-monitor (A 股)
- market-environment-analysis (市场环境)

---

#### 3. backtest-expert ⭐⭐⭐⭐

**用途**: 交易策略回测指导

**使用场景**:
- 策略开发
- 回测验证
- 参数优化
- 过拟合检测

**触发词**:
- "回测"
- "策略验证"
- "参数优化"
- "过拟合"

**调用方式**:
```bash
@ClawBreaker 这个策略怎么回测？
```

**协同 Skill**:
- dashboard (回测结果展示)
- data-analysis (数据分析)

---

#### 4. trading ⭐⭐⭐⭐

**用途**: 交易分析教育

**使用场景**:
- 技术分析
- 图表模式
- 风险管理
- 仓位计算

**触发词**:
- "技术分析"
- "图表模式"
- "风险管理"
- "仓位"

**协同 Skill**:
- backtest-expert (策略验证)
- financial-calculator (仓位计算)

---

#### 5. day-trading-skill ⭐⭐⭐

**用途**: 日内交易指导

**使用场景**:
- 日内交易策略
- 价格行为分析
- 风险管理

**触发词**:
- "日内交易"
- "价格行为"
- "短线交易"

---

#### 6. financial-agent-core ⭐⭐⭐⭐⭐

**用途**: 金融 Agent 核心整合层

**使用场景**:
- 统一调度 23 个投资技能
- Marcus 人设执行
- 投资决策

**触发词**:
- "投资建议"
- "投资组合"
- "资产配置"

**协同 Skill**:
- 所有金融类 Skill

---

#### 7. financial-calculator ⭐⭐⭐⭐

**用途**: 金融计算器

**使用场景**:
- 复利计算
- 现值/终值
- 折扣计算
- 定价策略

**触发词**:
- "复利计算"
- "现值"
- "定价"
- "投资回报"

---

#### 8. stock-analysis ⭐⭐⭐⭐

**用途**: 股票加密货币分析

**使用场景**:
- 基本面分析
- 技术面分析
- 股票对比
- 投资组合管理

**触发词**:
- "股票分析"
- "基本面"
- "技术面"
- "投资组合"

---

#### 9. stock-info-explorer ⭐⭐⭐⭐

**用途**: Yahoo Finance 股票分析

**使用场景**:
- 实时报价
- 图表生成
- 基本面摘要
- 一键报告

**触发词**:
- "股票报告"
- "K 线图"
- "基本面摘要"

---

#### 10. us-stock-analysis ⭐⭐⭐⭐

**用途**: 美股综合分析

**使用场景**:
- 美股基本面分析
- 技术面分析
- 股票对比
- 投资建议

**触发词**:
- "美股分析"
- "AAPL 怎么样"
- "TSLA vs NVDA"

---

#### 11. yahoo-finance ⭐⭐⭐⭐

**用途**: Yahoo Finance 数据

**使用场景**:
- 股票价格
- 财报数据
- 期权数据
- 股息数据

**触发词**:
- "Yahoo Finance"
- "股息"
- "期权"

---

#### 12. tushare-finance ⭐⭐⭐⭐

**用途**: 中国金融市场数据

**使用场景**:
- A 股数据
- 港股数据
- 美股数据
- 宏观数据 (GDP/CPI)

**触发词**:
- "A 股数据"
- "宏观数据"
- "GDP"
- "CPI"

**协同 Skill**:
- a-stock-monitor (监控)
- dashboard (展示)

---

#### 13. trading-coach ⭐⭐⭐⭐

**用途**: AI 交易复盘教练

**使用场景**:
- 交易 CSV 分析
- 交易表现评估
- 交易质量评分
- 复盘报告生成

**触发词**:
- "交易复盘"
- "分析我的交易"
- "交易 CSV"
- "盈亏统计"

---

#### 14. cfo ⭐⭐⭐

**用途**: 首席财务官

**使用场景**:
- 财务规划
- 现金管理
- 融资策略
- 资本分配

**触发词**:
- "财务规划"
- "现金流"
- "融资"

---

#### 15. economic-calendar-fetcher ⭐⭐⭐

**用途**: 经济日历获取

**使用场景**:
- 经济数据发布
- 央行会议
- 财报季

**触发词**:
- "经济日历"
- "财报季"
- "央行会议"

---

### 二、飞书集成类 (9 个)

#### 1. feishu-bitable ⭐⭐⭐⭐⭐

**用途**: 飞书多维表格管理

**使用场景**:
- 创建多维表格
- 管理记录 (增删改查)
- 管理字段/视图
- 批量导入数据

**触发词**:
- "多维表格"
- "bitable"
- "数据表"
- "记录"
- "字段"

**调用方式**:
```bash
@ClawSupport 创建一个股票跟踪表格
```

---

#### 2. feishu-calendar ⭐⭐⭐⭐⭐

**用途**: 飞书日历日程管理

**使用场景**:
- 查看日程
- 创建会议
- 修改日程
- 忙闲查询

**触发词**:
- "日程"
- "会议"
- "日历"
- "约会议"
- "忙闲"

---

#### 3. feishu-task ⭐⭐⭐⭐⭐

**用途**: 飞书任务管理

**使用场景**:
- 创建任务
- 查询任务
- 更新任务
- 任务清单管理

**触发词**:
- "任务"
- "待办"
- "to-do"
- "清单"

---

#### 4. feishu-doc-manager ⭐⭐⭐⭐

**用途**: 飞书文档管理

**使用场景**:
- Markdown 发布到飞书文档
- 表格转换
- 权限管理
- 批量写入

**触发词**:
- "飞书文档"
- "发布文档"
- "云文档"

---

#### 5. feishu-drive ⭐⭐⭐

**用途**: 飞书云空间文件管理

**使用场景**:
- 文件列表
- 文件上传/下载
- 文件复制/移动

**触发词**:
- "云空间"
- "云盘"
- "文件"

---

#### 6. feishu-memory-recall ⭐⭐⭐

**用途**: 飞书跨群记忆共享

**使用场景**:
- 跨群记忆
- 记忆搜索
- 事件共享

**触发词**:
- "记忆"
- "跨群"
- "共享"

---

#### 7. feishu-messaging ⭐⭐⭐⭐

**用途**: 飞书消息发送

**使用场景**:
- 查找群成员
- 查找群 ID
- 发送消息

**触发词**:
- "发消息"
- "群成员"
- "群 ID"

---

#### 8. feishu ⭐⭐⭐⭐⭐

**用途**: 飞书综合技能

**使用场景**:
- 用户搜索
- 群聊管理
- 消息管理

**触发词**:
- "飞书"
- "搜索用户"
- "群聊"

---

#### 9. gog ⭐⭐⭐

**用途**: Google Workspace CLI

**使用场景**:
- Gmail
- Google Calendar
- Google Drive
- Google Sheets
- Google Docs

**触发词**:
- "Google"
- "Gmail"
- "Google 日历"

---

### 三、数据分析类 (5 个)

#### 1. data-analysis ⭐⭐⭐⭐⭐

**用途**: 数据分析决策

**使用场景**:
- 统计分析
- 数据解读
- 决策支持

**触发词**:
- "数据分析"
- "统计"
- "数据解读"

---

#### 2. dashboard ⭐⭐⭐⭐⭐

**用途**: 自定义数据看板

**使用场景**:
- 数据可视化
- 本地托管
- 视觉 QA

**触发词**:
- "看板"
- "dashboard"
- "可视化"

**协同 Skill**:
- a-stock-monitor (数据源)
- data-analysis (分析)

---

#### 3. financial-calculator ⭐⭐⭐⭐

**用途**: 金融计算器

**使用场景**:
- 未来值计算
- 现值计算
- 复利计算

**触发词**:
- "计算"
- "复利"
- "现值"

---

#### 4. market-analysis-cn ⭐⭐⭐⭐

**用途**: 市场分析服务

**使用场景**:
- 企业市场趋势分析
- 竞品分析
- 用户行为洞察

**触发词**:
- "市场分析"
- "竞品分析"
- "market analysis"
- "趋势"

---

#### 5. market-environment-analysis ⭐⭐⭐⭐⭐

**用途**: 全球市场环境分析

**使用场景**:
- 全球市场分析 (美/欧/亚)
- 外汇/商品分析
- 经济指标解读
- 风险偏好评估

**触发词**:
- "市场环境"
- "全球市场"
- "相場環境"
- "市場分析"

---

### 四、工具效率类 (10 个)

#### 1. find-skills ⭐⭐⭐⭐

**用途**: Skill 发现安装

**使用场景**:
- 搜索 Skill
- 安装 Skill
- 更新 Skill

**触发词**:
- "找个 skill"
- "安装 skill"
- "有这个 skill 吗"

---

#### 2. agent-browser ⭐⭐⭐⭐

**用途**: 浏览器自动化

**使用场景**:
- 网页导航
- 点击/输入
- 页面快照

**触发词**:
- "浏览器"
- "打开网页"
- "截图"

---

#### 3. agency-agents-openclaw ⭐⭐⭐⭐⭐

**用途**: 61 个专业 AI Agent

**使用场景**:
- 单 Agent 专业任务
- 多 Agent 协作
- 部门协作

**触发词**:
- "Agent"
- "编排"
- "部门协作"

**协同 Skill**:
- clawsquad (角色分工)

---

#### 4. clawsquad ⭐⭐⭐⭐⭐

**用途**: 7 角色产研团队

**使用场景**:
- 需求评审
- 产品设计
- 开发测试
- 运维部署

**触发词**:
- "ClawSquad"
- "产研团队"
- "需求评审"

---

#### 5. clawmarketer ⭐⭐⭐⭐

**用途**: 市场增长官

**使用场景**:
- 市场营销
- 内容创作
- 社群运营

**触发词**:
- "营销"
- "推广"
- "内容创作"

---

#### 6. clawcoordinator ⭐⭐⭐⭐

**用途**: 项目协调员

**使用场景**:
- 项目管理
- 跨部门协调
- 流程优化

**触发词**:
- "项目协调"
- "流程"
- "进度"

---

#### 7. clawsupport ⭐⭐⭐⭐

**用途**: 运营支持官

**使用场景**:
- 客户服务
- 数据分析
- 财务追踪
- 合规支持

**触发词**:
- "运营"
- "客服"
- "报表"

---

#### 8. backtest-expert ⭐⭐⭐⭐

**用途**: 回测专家

**使用场景**:
- 策略回测
- 参数优化
- 过拟合检测

**触发词**:
- "回测"
- "策略验证"

---

#### 9. healthcheck ⭐⭐⭐

**用途**: 主机安全检查

**使用场景**:
- 安全审计
- 防火墙/SSH 加固
- 风险 posture

**触发词**:
- "安全检查"
- "加固"
- "审计"

---

#### 10. skill-creator ⭐⭐⭐

**用途**: Skill 创建更新

**使用场景**:
- 设计 Skill
- 打包 Skill
- 发布 Skill

**触发词**:
- "创建 skill"
- "打包 skill"

---

### 五、其他类 (13 个)

#### 1. video-frames ⭐⭐

**用途**: 视频帧提取

**触发词**: "视频" "提取帧" "ffmpeg"

#### 2. weather ⭐⭐⭐

**用途**: 天气预报

**触发词**: "天气" "气温" "预报"

#### 3. remotion-best-practices ⭐⭐

**用途**: Remotion 视频创建

**触发词**: "Remotion" "视频" "React"

#### 4. self-improvement ⭐⭐⭐⭐⭐

**用途**: 自我改进

**触发词**: "学习" "改进" "错误"

#### 5. skill-vetter ⭐⭐⭐

**用途**: Skill 安全审查

**触发词**: "skill 安全" "审查"

#### 6. product-agent ⭐⭐⭐⭐

**用途**: 产品 Agent

**触发词**: "产品" "需求" "PRD"

#### 7. proactive-agent ⭐⭐⭐⭐⭐

**用途**: 主动驱动 Agent

**触发词**: "主动" "自动化" "cron"

#### 8. news-summary ⭐⭐⭐

**用途**: 新闻摘要

**触发词**: "新闻" "摘要" "日报"

#### 9. polymarket-odds ⭐⭐⭐

**用途**: Polymarket 赔率

**触发词**: "赔率" "预测市场" "Polymarket"

#### 10. mem0 ⭐⭐⭐

**用途**: Mem0 记忆层

**触发词**: "记忆" "Mem0" "语义搜索"

#### 11. dashboard ⭐⭐⭐⭐⭐

**用途**: 数据看板

**触发词**: "看板" "可视化"

#### 12. data-analysis ⭐⭐⭐⭐⭐

**用途**: 数据分析

**触发词**: "数据分析" "统计"

#### 13. financial-agent-core ⭐⭐⭐⭐⭐

**用途**: 金融 Agent 核心

**触发词**: "金融" "投资" "Marcus"

---

## 🎯 Skill 智能调度机制

### 决策树

```
任务下达
  │
  ▼
任务分类
  │
  ├── 金融投资 → financial-agent-core (总调度)
  │               ├── A 股 → a-stock-monitor + tushare-finance
  │               ├── 美股 → finnhub-pro + us-stock-analysis
  │               ├── 回测 → backtest-expert + dashboard
  │               └── 交易 → trading-coach + trading
  │
  ├── 飞书操作 → feishu (总调度)
  │               ├── 文档 → feishu-doc-manager
  │               ├── 日历 → feishu-calendar
  │               ├── 任务 → feishu-task
  │               └── 表格 → feishu-bitable
  │
  ├── 数据分析 → data-analysis + dashboard
  │
  ├── 市场研究 → market-environment-analysis + market-analysis-cn
  │
  ├── 项目管理 → clawcoordinator + agency-agents
  │
  └── 其他 → find-skills (查找合适 Skill)
```

### 协同验证机制

```
复杂任务
  │
  ├── 主 Skill 执行
  │
  ├── 协同 Skill 验证
  │
  └── 结果对比
      ├── 一致 → 输出结果
      └── 不一致 → 人工复核
```

---

## 📊 Skill 使用频率统计

| Skill | 使用频率 | 优先级 | 自动化 |
|-------|---------|--------|--------|
| a-stock-monitor | 每日 | P0 | ✅ Cron |
| feishu-calendar | 每日 | P0 | ✅ Cron |
| feishu-task | 每日 | P0 | - |
| financial-agent-core | 每日 | P0 | - |
| market-environment-analysis | 每周 | P1 | - |
| dashboard | 每周 | P1 | - |
| backtest-expert | 按需 | P2 | - |
| clawcoordinator | 每日 | P0 | - |

---

## 🔄 Skill 更新机制

### 自动更新

```bash
# 每周一检查更新
skillhub sync
clawhub sync
```

### 手动安装

```bash
# 搜索 Skill
skillhub search <keywords>

# 安装 Skill
skillhub install <skill-name>
```

---

## 📚 相关文档

- [Skill 创建规范](../skills/skill-creator/SKILL.md)
- [Skill 安全审查](../skills/skill-vetter/SKILL.md)
- [Skill 发现安装](../skills/find-skills/SKILL.md)

---

**手册版本**: v1.0  
**创建日期**: 2026-03-16  
**维护者**: ClawCoordinator + Rex  
**下次更新**: 2026-04-16

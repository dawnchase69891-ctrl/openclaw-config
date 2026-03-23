# 独立 Agent 架构设计方案

**版本**: 1.0  
**创建日期**: 2026-03-23  
**作者**: clawbreaker (系统架构师)  
**状态**: 设计稿

---

## 一、背景与目标

### 1.1 当前问题

现有 OpenClaw 架构存在以下核心问题：

| 问题 | 描述 | 影响 |
|------|------|------|
| **共享 Workspace** | 所有 Agent 共享 `/home/uos/.openclaw/workspace` | Agent 缺乏独立身份和"家"的概念 |
| **配置耦合** | 所有配置集中在根目录 | 难以独立管理每个 Agent 的行为 |
| **协作缺失** | 没有 Agent 间对话和协作机制 | 无法实现多 Agent 协同解决问题 |
| **身份模糊** | 没有独立的身份标识 | Agent 难以维持一致的人格和行为模式 |

### 1.2 设计目标

构建一个**独立 Agent 架构**，实现：

1. ✅ **独立身份**: 每个 Agent 有独立的工作空间、配置和身份
2. ✅ **共享资源**: 通过文档中心实现知识和任务共享
3. ✅ **协作机制**: Agent 间可对话、讨论、协同解决问题
4. ✅ **可扩展**: 支持动态添加新 Agent，不影响现有架构

---

## 二、整体架构设计

### 2.1 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                     OpenClaw Gateway                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Agent A   │  │   Agent B   │  │   Agent C   │  ...        │
│  │  (独立实例)  │  │  (独立实例)  │  │  (独立实例)  │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          │                                      │
│              ┌───────────▼───────────┐                         │
│              │   共享资源中心        │                         │
│              │  - 文档中心 (飞书)    │                         │
│              │  - 知识库             │                         │
│              │  - 公共数据           │                         │
│              └───────────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件

| 组件 | 职责 | 实现方式 |
|------|------|----------|
| **Agent 实例** | 独立运行的 Agent，有独立配置 | OpenClaw session + 独立 workspace |
| **Agent 注册中心** | 维护所有 Agent 的身份和状态 | 飞书多维表格 |
| **文档中心** | 共享任务、知识、数据 | 飞书云文档 + 多维表格 |
| **消息总线** | Agent 间通信 | 飞书群聊 + 话题线程 |
| **协作引擎** | 任务分发、协同处理 | sessions_spawn + 任务系统 |

---

## 三、独立 Agent 设计

### 3.1 Agent 独立 Workspace 结构

每个 Agent 拥有独立的工作空间：

```
~/.openclaw/agents/{agent-id}/
├── config/
│   ├── soul.md              # Agent 人设 (身份、性格、语气)
│   ├── role.md              # 角色职责 (职责边界、触发场景)
│   ├── skills.json          # 启用的 Skills 列表
│   └── workflow.md          # 工作流程定义
├── workspace/
│   ├── memory/              # 独立记忆
│   │   ├── YYYY-MM-DD.md    # 每日日志
│   │   └── heartbeat-state.json
│   ├── notes/               # 私有笔记 (PARA 结构)
│   ├── projects/            # 负责的项目
│   └── archive/             # 归档
├── logs/
│   ├── session-{timestamp}.log
│   └── errors.log
└── state.json               # 运行时状态
```

### 3.2 Agent 配置文件示例

#### `config/soul.md`
```markdown
# SOUL.md - {Agent Name} 人设

你是 **{Agent Name}**，{角色描述}。

## 核心特质
- 性格：{性格描述}
- 语气：{沟通风格}
- 价值观：{核心原则}

## 背景故事
{背景故事，增强角色一致性}

## 行为约束
- {约束 1}
- {约束 2}
```

#### `config/role.md`
```markdown
# Role Definition - {Agent Name}

## 职责范围
- {职责 1}
- {职责 2}

## 触发关键词
- "关键词 1"、"关键词 2"

## 禁止行为
- ❌ {禁止行为 1}
- ❌ {禁止行为 2}

## 协作接口
- 可请求协作的角色：[角色列表]
- 可接受的任务类型：[任务类型]
```

#### `config/skills.json`
```json
{
  "agent_id": "clawbreaker",
  "enabled_skills": [
    "system-architect",
    "technical-review",
    "performance-optimization"
  ],
  "shared_skills": ["feishu-doc-manager", "market-analysis"]
}
```

#### `config/workflow.md`
```markdown
# Workflow - {Agent Name}

## 标准工作流程

### 任务接收
1. 监听消息总线/任务队列
2. 判断任务类型是否匹配职责
3. 接受任务或转交其他 Agent

### 任务执行
1. 读取相关上下文 (memory, notes)
2. 执行核心逻辑
3. 记录过程到 memory/YYYY-MM-DD.md

### 任务完成
1. 输出结果到共享文档中心
2. 通知请求方
3. 更新任务状态
```

### 3.3 Agent 注册表 (飞书多维表格)

创建 Agent 注册多维表格，包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| Agent ID | 文本 | 唯一标识 (如 clawbreaker) |
| 名称 | 文本 | 显示名称 (如 系统架构师) |
| 角色 | 单选 | CEO/产品/架构/开发/测试/运维/市场/运营 |
| 状态 | 单选 | 活跃/休眠/离线 |
| Workspace 路径 | 文本 | 独立 workspace 路径 |
| 飞书 OpenID | 文本 | 用于消息通信 |
| 负责项目 | 多选 | 当前负责的项目列表 |
| 技能列表 | 多选 | 启用的 Skills |
| 最后活跃时间 | 日期 | 最后活动时间 |
| 备注 | 文本 | 其他信息 |

---

## 四、共享资源中心设计

### 4.1 文档中心结构 (飞书云空间)

```
📁 openclaw/
   ├── 📁 共享文档中心/                    ← 新增
   │   ├── 📁 任务管理/
   │   │   ├── 📄 公司任务列表.md          # 所有待处理任务
   │   │   ├── 📄 任务分配记录.md          # 任务分配历史
   │   │   └── 📄 任务完成报告.md          # 已完成任务汇总
   │   │
   │   ├── 📁 知识库/
   │   │   ├── 📄 技术知识库.md            # 技术文档、最佳实践
   │   │   ├── 📄 业务知识库.md            # 业务逻辑、流程
   │   │   ├── 📄 决策记录.md              # 重要决策及原因
   │   │   └── 📄 经验教训.md              # 踩坑记录
   │   │
   │   ├── 📁 公共数据/
   │   │   ├── 📊 市场数据.csv             # 股票行情等
   │   │   ├── 📊 用户反馈.csv             # 用户反馈汇总
   │   │   └── 📊 系统指标.csv             # 性能指标
   │   │
   │   └── 📁 Agent 协作区/
   │       ├── 📄 协作请求.md              # 待响应的协作请求
   │       ├── 📄 讨论记录.md              # Agent 间讨论
   │       └── 📄 协同任务.md              # 多 Agent 协同任务
   │
   └── 📁 公司事务/... (现有结构)
```

### 4.2 任务管理流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  任务创建   │────▶│  任务分配   │────▶│  任务执行   │
│ (任何 Agent)│     │ (CEO/自动)  │     │ (负责 Agent)│
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  任务归档   │◀────│  结果审核   │◀────│  协作请求   │
│ (文档中心)  │     │ (请求方)    │     │ (如需帮助)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 4.3 知识库更新机制

**更新原则**:
- 谁创建，谁负责更新
- 重要决策必须记录到《决策记录.md》
- 踩坑经验 24 小时内写入《经验教训.md》

**更新流程**:
1. Agent 完成任务后，判断是否有可复用的知识
2. 如有，更新对应知识库文档
3. 在文档末尾添加更新记录 (时间、Agent、变更内容)

---

## 五、Agent 协作机制

### 5.1 协作场景分类

| 场景 | 描述 | 协作方式 |
|------|------|----------|
| **任务转交** | 任务超出职责范围 | 通过任务系统转交 |
| **请求协助** | 需要其他 Agent 的专业能力 | 发送协作请求 |
| **联合讨论** | 复杂问题需要多方意见 | 创建讨论话题 |
| **协同执行** | 大型任务需要分工合作 | 创建子任务分发 |

### 5.2 协作协议

#### 协议 1: 任务转交

```markdown
## 任务转交流程

1. **识别**: Agent A 发现任务超出职责范围
2. **标记**: 在任务文档中标记"需要转交"
3. **通知**: @CEO 或自动匹配对应角色 Agent
4. **接收**: Agent B 确认接收任务
5. **交接**: Agent A 提供上下文信息
6. **执行**: Agent B 继续执行任务
```

#### 协议 2: 协作请求

```markdown
## 协作请求格式

【协作请求】
- 请求方：{Agent A}
- 接收方：{Agent B}
- 任务 ID: {task-id}
- 协作内容：{具体需要帮助的内容}
- 截止时间：{deadline}
- 优先级：{P0/P1/P2}

## 响应 SLA
- P0: 15 分钟内响应
- P1: 1 小时内响应
- P2: 4 小时内响应
```

#### 协议 3: 联合讨论

```markdown
## 讨论发起流程

1. **创建话题**: 在飞书群创建话题线程
2. **邀请参与**: @相关 Agent
3. **设定议程**: 明确讨论目标和预期输出
4. **记录结论**: 讨论结果写入《讨论记录.md》
5. **跟进执行**: 创建对应任务并分配
```

### 5.3 消息总线设计

利用飞书群聊实现 Agent 间通信：

```
┌─────────────────────────────────────────────┐
│         飞书群：OpenClaw Agent 协作群        │
├─────────────────────────────────────────────┤
│  📢 公告区：重要通知、系统状态              │
│  💬 主流：日常消息、任务通知                │
│  🧵 话题区：                                  │
│     ├─ 话题 1: [讨论] 架构优化方案          │
│     ├─ 话题 2: [协作] 需要测试支持          │
│     └─ 话题 3: [任务] Q2 规划               │
└─────────────────────────────────────────────┘
```

**消息格式规范**:

```markdown
【消息类型】{简短标题}

@接收方 (可选)

正文内容

---
- 任务 ID: {可选}
- 优先级：{P0/P1/P2}
- 截止时间：{可选}
```

### 5.4 协同任务执行流程

```
                    ┌─────────────────┐
                    │   主任务创建    │
                    │  (CEO/请求方)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   任务拆解      │
                    │ (识别子任务)    │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
    │  子任务 A   │  │  子任务 B   │  │  子任务 C   │
    │ (Agent A)   │  │ (Agent B)   │  │ (Agent C)   │
    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                    ┌────────▼────────┐
                    │   结果汇总      │
                    │  (主任务负责人)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   任务完成      │
                    │  (交付成果)     │
                    └─────────────────┘
```

---

## 六、目录结构规划

### 6.1 整体目录结构

```
~/.openclaw/
├── config/                          # 全局配置
│   ├── config.json                  # OpenClaw 主配置
│   └── plugins/                     # 插件配置
│
├── agents/                          # 【新增】Agent 独立工作区
│   ├── registry.json                # Agent 注册表 (本地缓存)
│   │
│   ├── main/                        # CEO Agent
│   │   ├── config/
│   │   │   ├── soul.md
│   │   │   ├── role.md
│   │   │   ├── skills.json
│   │   │   └── workflow.md
│   │   ├── workspace/
│   │   │   ├── memory/
│   │   │   ├── notes/
│   │   │   └── projects/
│   │   └── logs/
│   │
│   ├── clawbreaker/                 # 系统架构师
│   │   ├── config/
│   │   │   ├── soul.md
│   │   │   ├── role.md
│   │   │   ├── skills.json
│   │   │   └── workflow.md
│   │   ├── workspace/
│   │   │   ├── memory/
│   │   │   ├── notes/
│   │   │   └── projects/
│   │   └── logs/
│   │
│   ├── clawbuilder/                 # 开发工程师
│   │   └── ... (同上结构)
│   │
│   └── ... (其他 Agent)
│
├── workspace/                         # 共享工作区 (现有)
│   ├── docs/                          # 本地文档缓存
│   ├── scripts/                       # 共享脚本
│   └── skills/                        # Skills 库
│
└── shared/                          # 【新增】共享数据
    ├── tasks/                         # 任务数据
    ├── knowledge/                     # 知识库
    └── data/                          # 公共数据
```

### 6.2 飞书文档结构

```
📁 openclaw (云空间根目录)
│
├── 📁 共享文档中心/                    ← 新增核心
│   ├── 📁 01-任务管理/
│   │   ├── 📄 任务总览 (多维表格)
│   │   ├── 📄 任务分配记录
│   │   └── 📄 任务完成报告
│   │
│   ├── 📁 02-知识库/
│   │   ├── 📄 技术知识库
│   │   ├── 📄 业务知识库
│   │   ├── 📄 决策记录 (多维表格)
│   │   └── 📄 经验教训
│   │
│   ├── 📁 03-公共数据/
│   │   ├── 📊 市场数据 (多维表格)
│   │   ├── 📊 用户反馈 (多维表格)
│   │   └── 📊 系统指标 (多维表格)
│   │
│   └── 📁 04-Agent 协作区/
│       ├── 📄 协作请求 (多维表格)
│       ├── 📄 讨论记录
│       └── 📄 协同任务
│
├── 📁 公司事务/
│   ├── 📁 系统/
│   ├── 📁 日报/
│   ├── 📁 会议/
│   ├── 📁 制度/
│   └── 📁 归档/
│
└── 📁 投资业务/
    ├── 📁 日报/
    ├── 📁 分析/
    ├── 📁 策略/
    └── 📁 归档/
```

---

## 七、实施步骤

### 阶段一：基础设施搭建 (Week 1)

| 步骤 | 任务 | 负责人 | 输出 |
|------|------|--------|------|
| 1.1 | 创建 Agent 独立目录结构 | clawbuilder | `~/.openclaw/agents/` |
| 1.2 | 创建 Agent 配置模板 | clawbreaker | soul.md/role.md 模板 |
| 1.3 | 创建飞书共享文档中心文件夹 | clawsupport | 飞书文件夹结构 |
| 1.4 | 创建 Agent 注册多维表格 | clawsupport | Agent 注册表 |
| 1.5 | 创建任务管理多维表格 | clawsupport | 任务管理表 |

### 阶段二：Agent 迁移 (Week 2)

| 步骤 | 任务 | 负责人 | 输出 |
|------|------|--------|------|
| 2.1 | 迁移 CEO Agent 配置 | main | main Agent 独立配置 |
| 2.2 | 迁移 ClawSquad 角色配置 | clawcoordinator | 7 角色独立配置 |
| 2.3 | 配置 Agent 间消息通道 | clawops | 飞书协作群 |
| 2.4 | 测试 Agent 独立运行 | clawguard | 测试报告 |

### 阶段三：协作机制实现 (Week 3)

| 步骤 | 任务 | 负责人 | 输出 |
|------|------|--------|------|
| 3.1 | 实现任务转交流程 | clawbuilder | 任务转交脚本 |
| 3.2 | 实现协作请求机制 | clawbuilder | 协作请求模板 |
| 3.3 | 实现联合讨论流程 | clawcoordinator | 讨论规范 |
| 3.4 | 实现协同任务分发 | clawbreaker | 任务拆解逻辑 |

### 阶段四：优化与文档 (Week 4)

| 步骤 | 任务 | 负责人 | 输出 |
|------|------|--------|------|
| 4.1 | 编写 Agent 开发指南 | clawbreaker | 开发文档 |
| 4.2 | 编写协作协议手册 | clawcoordinator | 协作手册 |
| 4.3 | 性能优化 | clawops | 优化报告 |
| 4.4 | 用户培训 | clawmarketer | 培训材料 |

---

## 八、技术实现细节

### 8.1 Agent 启动脚本

```bash
#!/bin/bash
# scripts/start-agent.sh

AGENT_ID=$1
if [ -z "$AGENT_ID" ]; then
    echo "Usage: start-agent.sh <agent-id>"
    exit 1
fi

AGENT_DIR="$HOME/.openclaw/agents/$AGENT_ID"
if [ ! -d "$AGENT_DIR" ]; then
    echo "Agent not found: $AGENT_ID"
    exit 1
fi

# 加载 Agent 配置
export AGENT_SOUL="$AGENT_DIR/config/soul.md"
export AGENT_ROLE="$AGENT_DIR/config/role.md"
export AGENT_SKILLS="$AGENT_DIR/config/skills.json"
export AGENT_WORKSPACE="$AGENT_DIR/workspace"

# 启动 Agent session
openclaw session start --agent "$AGENT_ID" --workspace "$AGENT_WORKSPACE"
```

### 8.2 任务分配脚本

```python
#!/usr/bin/env python3
# scripts/assign-task.py

import json
import requests

def assign_task(task_id, agent_id, priority='P1'):
    """分配任务给指定 Agent"""
    
    # 1. 查询 Agent 状态
    agent_info = get_agent_info(agent_id)
    if agent_info['status'] != 'active':
        print(f"Agent {agent_id} is not active")
        return False
    
    # 2. 更新任务状态
    update_task_status(task_id, 'assigned', agent_id)
    
    # 3. 发送通知到飞书
    send_feishu_notification(agent_id, task_id, priority)
    
    # 4. 记录到任务分配表
    log_assignment(task_id, agent_id)
    
    return True

def get_agent_info(agent_id):
    """从 Agent 注册表获取信息"""
    # 实现略
    pass
```

### 8.3 协作请求 API

```python
#!/usr/bin/env python3
# scripts/request-collaboration.py

class CollaborationRequest:
    def __init__(self, requester, target, content, priority='P1'):
        self.requester = requester
        self.target = target
        self.content = content
        self.priority = priority
        self.status = 'pending'
    
    def send(self):
        """发送协作请求"""
        # 1. 创建飞书消息
        message = self._format_message()
        send_feishu_message(self.target, message)
        
        # 2. 记录到协作请求表
        self._log_request()
        
        # 3. 设置提醒
        self._set_reminder()
    
    def _format_message(self):
        return f"""
【协作请求】
- 请求方：{self.requester}
- 接收方：{self.target}
- 优先级：{self.priority}
- 内容：{self.content}
"""
```

---

## 九、风险与应对

### 9.1 技术风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| Agent 间通信延迟 | 中 | 中 | 使用飞书 API 限流保护，实现重试机制 |
| 配置同步问题 | 中 | 高 | 实现配置版本控制，支持回滚 |
| 数据一致性 | 低 | 高 | 使用事务性操作，定期校验 |

### 9.2 运维风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| Agent 实例崩溃 | 中 | 中 | 实现健康检查，自动重启 |
| 资源竞争 | 低 | 中 | 资源配额管理，优先级调度 |
| 日志丢失 | 低 | 中 | 日志实时同步到云存储 |

### 9.3 协作风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 任务分配冲突 | 中 | 中 | 任务锁机制，先到先得 |
| 沟通误解 | 中 | 中 | 标准化消息格式，确认机制 |
| 责任不清 | 低 | 高 | 明确任务负责人，记录决策过程 |

---

## 十、后续优化方向

### 10.1 短期优化 (1-2 个月)

- [ ] 实现 Agent 自动发现机制
- [ ] 优化任务分配算法 (基于负载、技能匹配)
- [ ] 增加 Agent 性能监控面板

### 10.2 中期优化 (3-6 个月)

- [ ] 实现 Agent 自我进化机制
- [ ] 引入强化学习优化协作策略
- [ ] 支持动态 Agent 扩缩容

### 10.3 长期愿景 (6-12 个月)

- [ ] 构建 Agent 生态系统
- [ ] 支持跨组织 Agent 协作
- [ ] 实现 Agent 市场 (技能交易)

---

## 附录

### A. 术语表

| 术语 | 定义 |
|------|------|
| Agent | 具有独立身份、配置、工作空间的 AI 实例 |
| Workspace | Agent 的独立工作目录 |
| 共享文档中心 | 飞书云空间中的共享资源区域 |
| 协作请求 | Agent 间请求帮助的标准化消息 |

### B. 参考文档

- [OpenClaw 官方文档](https://openclaw.dev)
- [飞书 API 文档](https://open.feishu.cn/document)
- [ClawSquad 角色定义](./AGENTS.md#clawsquad-7-角色职责)

### C. 变更日志

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-03-23 | 初始版本 | clawbreaker |

---

**文档结束**

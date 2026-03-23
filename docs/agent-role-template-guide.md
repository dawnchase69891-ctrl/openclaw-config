# Agent 角色定义模板使用指南

**版本**: 1.0.0  
**创建日期**: 2026-03-20  
**维护人**: ClawBuilder (开发工程师) 💻

---

## 快速开始

### 1. 查看可用模板

```bash
cd /home/uos/.openclaw/workspace
python3 scripts/agent_role_template.py list-templates
```

输出示例:
```
可用 Agent 角色模板:

  - clawbreaker: ClawBreaker (系统架构师)
  - clawbuilder: ClawBuilder (高级开发工程师)
  - clawcoordinator: ClawCoordinator (项目协调员)
  - ... (共 12 个角色)
```

### 2. 生成单个 Agent 的 SOUL.md

```bash
# 生成到默认位置 (~/.openclaw/agents/{id}/agent/SOUL.md)
python3 scripts/agent_role_template.py generate --agent-id clawbuilder

# 生成到指定路径
python3 scripts/agent_role_template.py generate --agent-id clawbuilder --output /tmp/SOUL.md
```

### 3. 验证 SOUL.md 完整性

```bash
# 验证单个 Agent
python3 scripts/agent_role_template.py validate --agent-dir /home/uos/.openclaw/agents/clawbuilder/agent

# 以 JSON 格式输出 (便于脚本处理)
python3 scripts/agent_role_template.py validate --agent-dir /home/uos/.openclaw/agents/clawbuilder/agent --json
```

### 4. 批量生成所有 Agent

```bash
# 批量生成到默认位置
python3 scripts/agent_role_template.py generate-all

# 批量生成到指定基础路径
python3 scripts/agent_role_template.py generate-all --output-base /tmp/agents
```

---

## 标准 SOUL.md 结构

```markdown
# SOUL.md - {Name} 人设

你是 **{Name}**，{Role}。

## Role (角色定位)
{一句话角色定位}

## Goal (核心目标)
{核心目标描述}

## Backstory (背景故事)
{背景故事，增强角色一致性}

## Constraints (约束条件)
- {约束 1}
- {约束 2}
- ...

## Skills (可用技能)
- **{skill-1}**: {描述}
- **{skill-2}**: {描述}
- ...

## 语气风格
- ✅ {正面特征 1}
- ✅ {正面特征 2}
- ❌ {负面特征}

## 触发场景
- "关键词 1"、"关键词 2"、...

## 典型输出
- {输出类型 1}
- {输出类型 2}
- ...

---

*最后更新：{日期} (Agent 角色定义框架实施)*
```

---

## ClawSquad 12 角色一览

| ID | 名称 | 角色 | 核心目标 |
|----|------|------|----------|
| **main** | 骐骥 (CEO) | 首席执行官 | 战略决策、任务分配、资源协调 |
| **rex** | Rex | 产品指挥官 | 产品战略、需求评审、优先级裁决 |
| **clawhunter** | ClawHunter | 需求分析师 | 用户调研、竞品分析、需求挖掘 |
| **clawdesigner** | ClawDesigner | 交互设计师 | 用户体验、视觉设计、交互优化 |
| **clawbreaker** | ClawBreaker | 系统架构师 | 架构设计、技术选型、性能优化 |
| **clawbuilder** | ClawBuilder | 高级开发工程师 | 功能实现、代码编写、单元测试 |
| **clawguard** | ClawGuard | 测试工程师 | 测试策略、性能压测、质量评审 |
| **clawops** | ClawOps | 运维工程师 | CI/CD、系统监控、故障应急 |
| **clawmarketer** | ClawMarketer | 市场增长官 | 品牌传播、内容创作、用户增长 |
| **clawcoordinator** | ClawCoordinator | 项目协调员 | 项目规划、资源协调、流程优化 |
| **clawsupport** | ClawSupport | 运营支持官 | 数据报表、财务追踪、合规检查 |
| **marcus** | Marcus | 高级投资分析师 | 股票分析、投资建议、交易复盘 |

---

## 验证规则

脚本会自动检查以下必需章节:

- ✅ `## Role` (或 `## Role (角色定位)`)
- ✅ `## Goal` (或 `## Goal (核心目标)`)
- ✅ `## Backstory` (或 `## Backstory (背景故事)`)
- ✅ `## Constraints` (或 `## Constraints (约束条件)`)
- ✅ `## Skills` (或 `## Skills (可用技能)`)

推荐章节 (缺少时会警告):

- ⚠️ `## 语气风格`
- ⚠️ `## 触发场景`
- ⚠️ `## 典型输出`

其他检查:

- ⚠️ 文件长度 < 500 字符 → 警告
- ⚠️ 无加粗格式 (`**`) → 警告 (技能列表可能格式不正确)

---

## 自定义角色

如需添加新角色或修改现有角色定义:

### 方法 1: 修改脚本中的角色库

编辑 `scripts/agent_role_template.py` 中的 `CLAWSQUAD_ROLES` 字典:

```python
CLAWSQUAD_ROLES = {
    "new-agent": {
        "name": "新 Agent 名称",
        "role": "角色名称",
        "role_description": "详细角色描述",
        "goal": "核心目标",
        "backstory": "背景故事",
        "constraints": ["约束 1", "约束 2", ...],
        "skills": [
            ("skill-id-1", "技能描述 1"),
            ("skill-id-2", "技能描述 2"),
            ...
        ],
        "tone_positive": ["正面特征 1", "正面特征 2", ...],
        "tone_negative": ["负面特征 1", "负面特征 2", ...],
        "triggers": ["触发词 1", "触发词 2", ...],
        "outputs": ["输出类型 1", "输出类型 2", ...]
    },
    # ... 其他角色
}
```

然后运行:
```bash
python3 scripts/agent_role_template.py generate --agent-id new-agent
```

### 方法 2: 手动创建 SOUL.md

直接编辑 `~/.openclaw/agents/{agent-id}/agent/SOUL.md`,遵循标准模板格式。

---

## 最佳实践

1. **保持角色边界清晰** - 每个 Agent 专注于自己的职责范围
2. **约束条件具体可执行** - 使用"❌ 不..."和"✅ 必须..."格式
3. **技能列表与实际配置一致** - 确保列出的技能已安装且可用
4. **定期更新** - 当 Agent 职责变化时及时更新 SOUL.md
5. **版本控制** - 使用 Git 管理 SOUL.md 变更历史

---

## 故障排查

### 问题 1: "未知 Agent ID"

```
❌ 错误：未知 Agent ID: xxx
```

**解决**: 使用 `list-templates` 查看可用的 Agent ID:
```bash
python3 scripts/agent_role_template.py list-templates
```

### 问题 2: 验证失败

```
❌ 缺少必需章节：## Goal
```

**解决**: 编辑 SOUL.md 添加缺失的章节，或使用 `generate` 命令重新生成。

### 问题 3: 权限错误

```
Permission denied: /home/uos/.openclaw/agents/xxx/agent/SOUL.md
```

**解决**: 确保脚本有执行权限:
```bash
chmod +x scripts/agent_role_template.py
```

---

## 相关文件

- **脚本**: `~/.openclaw/workspace/scripts/agent_role_template.py`
- **实施日志**: `~/.openclaw/workspace/notes/implementation-log.md`
- **规范文档**: `~/.openclaw/workspace/AGENTS.md` (角色定义框架章节)
- **Agent 目录**: `~/.openclaw/agents/{agent-id}/agent/SOUL.md`

---

## 变更历史

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-03-20 | 1.0.0 | 初始版本，包含 12 个 ClawSquad 角色定义 |

---

*最后更新：2026-03-20*

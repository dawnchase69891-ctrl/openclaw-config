# 🤝 ClawSquad × Claude Code 协同方案

**版本**: v1.0  
**创建时间**: 2026-03-16  
**作者**: 骐骥 (Qíjì) 🐎 (CEO)

---

## 🎯 协同定位

**ClawSquad** (自主产研团队) + **Claude Code** (AI 编程助手) = 人机协作研发新模式

### 核心价值
- 🚀 **ClawSquad**: 提供全流程产研能力 (需求→设计→开发→测试→运维)
- ⚡ **Claude Code**: 提供专业代码生成、审查、重构能力
- 🎯 **协同效应**: 人类智慧 + AI 效率 = 10 倍研发生产力

---

## 📋 协同模式

### 模式 1: ClawSquad 主导 + Claude Code 辅助

```
┌─────────────────────────────────────────────────────────┐
│  ClawSquad 角色              Claude Code 职责            │
├─────────────────────────────────────────────────────────┤
│  Rex (产品指挥官)           需求可行性分析              │
│  ClawHunter (需求)          用户故事生成                │
│  ClawDesigner (设计)        设计稿代码转换              │
│  ClawBreaker (架构)         架构方案评审                │
│  ClawBuilder (开发)  ────→  代码生成/审查/重构  ◄────   │
│  ClawGuard (测试)           测试用例生成                │
│  ClawOps (运维)             部署脚本/监控配置           │
└─────────────────────────────────────────────────────────┘
```

**适用场景**:
- 日常功能开发
- 代码审查与重构
- 测试用例补充
- 文档生成

---

### 模式 2: Claude Code 主导 + ClawSquad 监督

```
┌─────────────────────────────────────────────────────────┐
│  Claude Code                 ClawSquad 职责              │
├─────────────────────────────────────────────────────────┤
│  代码生成        ────→       ClawBuilder 审查           │
│  自动重构                    ClawBreaker 把关            │
│  单元测试                    ClawGuard 验证              │
│  文档编写                    Rex 最终审批                │
└─────────────────────────────────────────────────────────┘
```

**适用场景**:
- 重复性代码生成
- 大规模重构
- 样板代码编写
- 紧急 Bug 修复

---

## 🔧 技术配置

### ✅ 当前配置状态 (2026-03-16 已配置)

```json5
{
  "acp": {
    "enabled": true,
    "dispatch": { "enabled": true },
    "allowedAgents": ["claude", "codex", "opencode", "gemini"],
    "defaultAgent": "claude"
  }
}
```

### 已安装组件

| 组件 | 版本 | 状态 |
|------|------|------|
| `openclaw-acp` | 0.0.6 | ✅ 已安装 |
| `acpx` | 0.3.0 | ✅ 已安装 |
| ACP 配置 | - | ✅ 已启用 |

### 配置说明

| 配置项 | 说明 | 当前值 |
|--------|------|--------|
| `acp.enabled` | 启用 ACP 后端 | `true` ✅ |
| `acp.dispatch.enabled` | 启用 ACP 分发 | `true` ✅ |
| `acp.allowedAgents` | 允许的 AI 编程助手 | `["claude", "codex", "opencode", "gemini"]` |
| `acp.defaultAgent` | 默认 AI 助手 | `"claude"` |

---

## 📖 使用流程

### 场景 1: 新功能开发

```
1. 骐骥 (CEO): "开发一个用户登录功能"
   ↓
2. Rex: "ClawHunter 做需求调研，ClawBreaker 评估技术方案"
   ↓
3. ClawHunter: 调研用户需求 → 输出 MRD
   ↓
4. ClawBreaker: 设计架构 → 调用 Claude Code 生成原型代码
   ↓
5. ClawBuilder: 审查代码 → 补充单元测试 → 调用 Claude Code 优化
   ↓
6. ClawGuard: 测试验证 → Bug 追踪 → 调用 Claude Code 修复
   ↓
7. ClawOps: CI/CD 部署 → 监控上线
   ↓
8. Rex: 审批通过 → 归档
```

**Claude Code 调用点**:
- 步骤 4: 生成原型代码
- 步骤 5: 代码优化
- 步骤 6: Bug 修复

---

### 场景 2: 代码审查

```
1. ClawBuilder: "提交 PR #123 - 用户认证模块"
   ↓
2. ClawGuard: "启动代码审查流程"
   ↓
3. Claude Code: 
   - 静态代码分析
   - 安全漏洞扫描
   - 性能问题检测
   - 测试覆盖率检查
   ↓
4. ClawBreaker: 审查 Claude Code 报告 → 提出改进建议
   ↓
5. ClawBuilder: 根据反馈修改 → 重新提交
   ↓
6. ClawGuard: 验证通过 → 批准合并
```

---

### 场景 3: 技术债务清理

```
1. ClawBreaker: "识别技术债务清单"
   ↓
2. Claude Code: 
   - 代码复杂度分析
   - 重复代码检测
   - 过时依赖识别
   ↓
3. Rex: 优先级排序 → 纳入 Sprint
   ↓
4. ClawBuilder + Claude Code: 
   - 结对重构
   - 自动修复
   ↓
5. ClawGuard: 回归测试验证
```

---

## 🎭 角色协同指南

### Rex (产品指挥官) × Claude Code

**协同方式**:
```
Rex: "Claude，评估这个需求的技术可行性"
Claude Code: 
  - 技术栈匹配度分析
  - 工作量估算
  - 风险点识别
Rex: 基于分析做出决策
```

**最佳实践**:
- ✅ 让 Claude Code 参与需求评审
- ✅ 用 AI 分析辅助决策
- ❌ 不要完全依赖 AI 判断

---

### ClawBuilder (开发工程师) × Claude Code

**协同方式**:
```
ClawBuilder: "实现用户认证模块"
Claude Code: 
  1. 生成基础代码框架
  2. 实现核心逻辑
  3. 编写单元测试
ClawBuilder: 
  1. 审查代码质量
  2. 优化业务逻辑
  3. 补充边界测试
```

**最佳实践**:
- ✅ AI 生成 + 人工审查
- ✅ 复杂逻辑人工实现
- ✅ 保持代码所有权意识

---

### ClawGuard (测试工程师) × Claude Code

**协同方式**:
```
ClawGuard: "生成测试用例"
Claude Code:
  - 单元测试 (覆盖率>80%)
  - 边界条件测试
  - 异常场景测试
ClawGuard:
  - 补充探索性测试
  - 验证 AI 生成的测试
  - 执行性能/安全测试
```

---

## 📊 协同效果评估

### 效率提升

| 任务类型 | 纯人工 | ClawSquad + Claude Code | 提升 |
|---------|--------|------------------------|------|
| 功能开发 | 100% | 40-60% | 40-60% ⬆️ |
| 代码审查 | 100% | 30-50% | 50-70% ⬆️ |
| 测试用例 | 100% | 20-40% | 60-80% ⬆️ |
| 文档编写 | 100% | 30-50% | 50-70% ⬆️ |
| Bug 修复 | 100% | 40-60% | 40-60% ⬆️ |

### 质量保障

| 指标 | 目标值 | 监控方式 |
|------|--------|---------|
| 代码审查覆盖率 | 100% | ClawGuard + Claude Code |
| 测试覆盖率 | >80% | Claude Code 生成 + ClawGuard 补充 |
| Bug 检出率 | >95% | 双保险 (AI + 人工) |
| 技术债务增长率 | <5%/月 | ClawBreaker 定期评估 |

---

## ⚠️ 风险控制

### AI 生成代码风险

| 风险 | 缓解措施 | 负责角色 |
|------|---------|---------|
| 安全漏洞 | ClawGuard 安全扫描 + 人工审查 | ClawGuard |
| 性能问题 | 性能测试 + ClawBreaker 把关 | ClawBreaker |
| 逻辑错误 | 单元测试 + 集成测试 | ClawBuilder + ClawGuard |
| 代码风格不一致 | ESLint/Prettier + 代码规范 | ClawBuilder |
| 过度依赖 AI | 定期人工代码审查 | Rex |

### 协同流程风险

| 风险 | 缓解措施 |
|------|---------|
| AI 理解偏差 | 明确需求描述 + 多轮确认 |
| 上下文丢失 | 使用持久会话 + 文档记录 |
| 权限滥用 | 限制 AI 工具权限 + 人工审批 |

---

## 🚀 快速开始

### 1. 配置 ACP

```bash
# 编辑配置文件
vim ~/.openclaw/openclaw.json

# 添加 ACP 配置
{
  "acp": {
    "enabled": true,
    "allowedAgents": ["claude"]
  }
}

# 重启 Gateway
openclaw gateway restart
```

### 2. 启动协同模式

```bash
# 方式 1: 使用 slash 命令
/acp spawn claude --mode persistent --thread auto

# 方式 2: 使用 sessions_spawn 工具
{
  "runtime": "acp",
  "agentId": "claude",
  "task": "协助开发用户登录功能"
}
```

### 3. 分配任务

```markdown
@ClawSquad 启动

骐骥 (CEO): "开发用户登录功能，ClawBuilder 主导，Claude Code 辅助"

Rex: "收到。ClawBuilder 负责实现，Claude Code 生成基础代码，
      ClawGuard 负责测试验证。"
```

---

## 📝 最佳实践

### ✅ 推荐做法

1. **明确分工**: AI 生成 + 人工审查
2. **渐进采用**: 从简单任务开始，逐步扩大范围
3. **持续学习**: 定期复盘 AI 协作效果
4. **文档记录**: 记录 AI 生成代码的审查意见
5. **权限控制**: 限制 AI 的生产环境访问

### ❌ 避免做法

1. **完全依赖**: 不经审查直接部署 AI 代码
2. **黑盒使用**: 不理解 AI 生成的代码逻辑
3. **权限过大**: 给 AI 过高的系统权限
4. **忽视安全**: 跳过安全扫描和测试

---

## 📈 持续改进

### 每周复盘

```
Rex 主持，全员参与:
1. 本周 AI 协作任务回顾
2. 效率提升数据分析
3. 质量问题讨论
4. 改进措施制定
```

### 月度优化

```
骐骥 (CEO) 主持:
1. 协同效果评估
2. 工具链优化
3. 流程改进
4. 培训计划
```

---

## 📚 参考资料

- [OpenClaw ACP Agents](https://docs.openclaw.ai/tools/acp-agents)
- [OpenClaw Sub-agents](https://docs.openclaw.ai/tools/subagents)
- [ClawSquad Skill](/home/uos/.openclaw/workspace/skills/clawsquad/SKILL.md)
- [Claude Code 官方文档](https://docs.anthropic.com/claude-code)

---

**维护者**: 骐骥 (Qíjì) 🐎 (CEO)  
**最后更新**: 2026-03-16  
**版本**: v1.0

---

## 🎯 下一步行动

- [ ] 配置 ACP 后端 (acpx 插件)
- [ ] 测试 ClawSquad + Claude Code 协同流程
- [ ] 编写具体场景的操作手册
- [ ] 收集团队反馈并优化流程

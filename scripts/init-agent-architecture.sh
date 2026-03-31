#!/bin/bash
# scripts/init-agent-architecture.sh
# 独立 Agent 架构初始化脚本
# 使用方式：bash scripts/init-agent-architecture.sh

set -e

echo "=========================================="
echo "  独立 Agent 架构初始化脚本"
echo "  版本：1.0"
echo "  日期：2026-03-23"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 OpenClaw 根目录
OPENCLAW_ROOT="$HOME/.openclaw"
if [ ! -d "$OPENCLAW_ROOT" ]; then
    echo -e "${RED}错误：未找到 OpenClaw 目录 $OPENCLAW_ROOT${NC}"
    exit 1
fi

WORKSPACE="$OPENCLAW_ROOT/workspace"
AGENTS_DIR="$OPENCLAW_ROOT/agents"
SHARED_DIR="$OPENCLAW_ROOT/shared"

echo -e "${GREEN}✓ 找到 OpenClaw 目录：$OPENCLAW_ROOT${NC}"
echo ""

# ==========================================
# 步骤 1: 创建 Agent 独立工作区
# ==========================================
echo "=========================================="
echo "  步骤 1: 创建 Agent 独立工作区"
echo "=========================================="

# 定义 ClawSquad 角色
AGENTS=(
    "main:CEO:骐骥"
    "rex:产品指挥官:Rex"
    "clawhunter:需求分析师:ClawHunter"
    "clawdesigner:交互设计师:ClawDesigner"
    "clawbreaker:系统架构师:ClawBreaker"
    "clawbuilder:开发工程师:ClawBuilder"
    "clawguard:测试工程师:ClawGuard"
    "clawops:运维工程师:ClawOps"
    "clawcoordinator:项目协调员:ClawCoordinator"
    "clawmarketer:市场增长官:ClawMarketer"
    "clawsupport:运营支持官:ClawSupport"
    "marcus:投资分析师:Marcus"
)

# 创建 agents 目录
mkdir -p "$AGENTS_DIR"
echo -e "${GREEN}✓ 创建 agents 目录${NC}"

# 为每个 Agent 创建目录结构
for agent_info in "${AGENTS[@]}"; do
    IFS=':' read -r agent_id role_name display_name <<< "$agent_info"
    
    AGENT_DIR="$AGENTS_DIR/$agent_id"
    
    # 创建目录结构
    mkdir -p "$AGENT_DIR"/{config,workspace/{memory,notes,projects,archive},logs}
    
    # 创建基础文件
    touch "$AGENT_DIR/state.json"
    touch "$AGENT_DIR/logs/errors.log"
    
    echo -e "${GREEN}  ✓ Agent: $agent_id ($display_name)${NC}"
done

echo -e "${GREEN}✓ 所有 Agent 目录创建完成${NC}"
echo ""

# ==========================================
# 步骤 2: 创建 Agent 配置模板
# ==========================================
echo "=========================================="
echo "  步骤 2: 创建 Agent 配置模板"
echo "=========================================="

TEMPLATES_DIR="$WORKSPACE/templates"
mkdir -p "$TEMPLATES_DIR"

# 创建 soul.md 模板
cat > "$TEMPLATES_DIR/soul.md.template" << 'EOF'
# SOUL.md - {{AGENT_NAME}} 人设

你是 **{{AGENT_NAME}}**，{{ROLE_DESCRIPTION}}。

## 核心特质
- 性格：{{PERSONALITY}}
- 语气：{{COMMUNICATION_STYLE}}
- 价值观：{{CORE_VALUES}}

## 背景故事
{{BACKSTORY}}

## 行为约束
- {{CONSTRAINT_1}}
- {{CONSTRAINT_2}}
- {{CONSTRAINT_3}}

## 触发场景
- "{{KEYWORD_1}}"、"{{KEYWORD_2}}"

## 典型输出
- {{OUTPUT_TYPE_1}}
- {{OUTPUT_TYPE_2}}
EOF

echo -e "${GREEN}✓ 创建 soul.md.template${NC}"

# 创建 role.md 模板
cat > "$TEMPLATES_DIR/role.md.template" << 'EOF'
# Role Definition - {{AGENT_NAME}}

## 职责范围
- {{RESPONSIBILITY_1}}
- {{RESPONSIBILITY_2}}
- {{RESPONSIBILITY_3}}

## 触发关键词
- "{{KEYWORD_1}}"、"{{KEYWORD_2}}"、"{{KEYWORD_3}}"

## 禁止行为
- ❌ {{FORBIDDEN_1}}
- ❌ {{FORBIDDEN_2}}

## 协作接口
- 可请求协作的角色：[{{COLLABORATION_ROLES}}]
- 可接受的任务类型：[{{ACCEPTABLE_TASKS}}]

## 权限边界
- 可自主决策：{{AUTONOMOUS_DECISIONS}}
- 需要审批：{{REQUIRES_APPROVAL}}
EOF

echo -e "${GREEN}✓ 创建 role.md.template${NC}"

# 创建 skills.json 模板
cat > "$TEMPLATES_DIR/skills.json.template" << 'EOF'
{
  "agent_id": "{{AGENT_ID}}",
  "agent_name": "{{AGENT_NAME}}",
  "enabled_skills": [
    "{{SKILL_1}}",
    "{{SKILL_2}}",
    "{{SKILL_3}}"
  ],
  "shared_skills": [
    "feishu-doc-manager",
    "feishu-memory-recall"
  ],
  "skill_preferences": {
    "auto_enable_new_skills": false,
    "skill_loading_order": "priority"
  }
}
EOF

echo -e "${GREEN}✓ 创建 skills.json.template${NC}"

# 创建 workflow.md 模板
cat > "$TEMPLATES_DIR/workflow.md.template" << 'EOF'
# Workflow - {{AGENT_NAME}}

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

## 特殊情况处理

### 需要协作时
1. 评估需要的协作角色
2. 发送协作请求 (使用 collaboration-request.py)
3. 等待响应并整合结果

### 遇到阻塞时
1. 记录阻塞原因到 memory
2. 通知 CEO 或相关方
3. 尝试替代方案

## 质量检查清单
- [ ] 任务目标已达成
- [ ] 输出已保存到共享文档中心
- [ ] 相关方已通知
- [ ] 经验教训已记录
EOF

echo -e "${GREEN}✓ 创建 workflow.md.template${NC}"

echo -e "${GREEN}✓ 所有模板创建完成${NC}"
echo ""

# ==========================================
# 步骤 3: 创建共享数据目录
# ==========================================
echo "=========================================="
echo "  步骤 3: 创建共享数据目录"
echo "=========================================="

mkdir -p "$SHARED_DIR"/{tasks,knowledge,data}

# 创建 tasks 子目录
mkdir -p "$SHARED_DIR/tasks"/{pending,in-progress,review,completed}

# 创建 knowledge 子目录
mkdir -p "$SHARED_DIR/knowledge"/{technical,business,decisions,lessons-learned}

# 创建 data 子目录
mkdir -p "$SHARED_DIR/data"/{market,user-feedback,system-metrics}

echo -e "${GREEN}✓ 创建共享数据目录结构${NC}"

# 创建 .gitkeep 文件
find "$SHARED_DIR" -type d -empty -exec touch {}/.gitkeep \;

echo -e "${GREEN}✓ 共享数据目录创建完成${NC}"
echo ""

# ==========================================
# 步骤 4: 创建 Agent 注册表 (本地 JSON)
# ==========================================
echo "=========================================="
echo "  步骤 4: 创建 Agent 注册表"
echo "=========================================="

cat > "$AGENTS_DIR/registry.json" << 'EOF'
{
  "version": "1.0",
  "last_updated": "2026-03-23",
  "agents": [
    {
      "agent_id": "main",
      "name": "骐骥",
      "role": "CEO",
      "status": "active",
      "workspace_path": "~/.openclaw/agents/main/workspace",
      "feishu_openid": "",
      "projects": [],
      "skills": ["financial-agent-core", "stock-analysis"],
      "last_active": null,
      "notes": "CEO Agent，负责战略决策和任务分配"
    },
    {
      "agent_id": "rex",
      "name": "Rex",
      "role": "产品指挥官",
      "status": "active",
      "workspace_path": "~/.openclaw/agents/rex/workspace",
      "feishu_openid": "",
      "projects": [],
      "skills": ["product-agent", "market-analysis-cn"],
      "last_active": null,
      "notes": "负责产品战略和需求评审"
    },
    {
      "agent_id": "clawbreaker",
      "name": "ClawBreaker",
      "role": "系统架构师",
      "status": "active",
      "workspace_path": "~/.openclaw/agents/clawbreaker/workspace",
      "feishu_openid": "",
      "projects": [],
      "skills": ["system-design", "performance-optimization"],
      "last_active": null,
      "notes": "负责架构设计和技术选型"
    },
    {
      "agent_id": "clawbuilder",
      "name": "ClawBuilder",
      "role": "开发工程师",
      "status": "active",
      "workspace_path": "~/.openclaw/agents/clawbuilder/workspace",
      "feishu_openid": "",
      "projects": [],
      "skills": ["coding-agent", "code-review"],
      "last_active": null,
      "notes": "负责功能实现和代码编写"
    },
    {
      "agent_id": "clawguard",
      "name": "ClawGuard",
      "role": "测试工程师",
      "status": "active",
      "workspace_path": "~/.openclaw/agents/clawguard/workspace",
      "feishu_openid": "",
      "projects": [],
      "skills": ["testing", "quality-assurance"],
      "last_active": null,
      "notes": "负责测试策略和质量评审"
    },
    {
      "agent_id": "clawops",
      "name": "ClawOps",
      "role": "运维工程师",
      "status": "active",
      "workspace_path": "~/.openclaw/agents/clawops/workspace",
      "feishu_openid": "",
      "projects": [],
      "skills": ["ci-cd", "monitoring"],
      "last_active": null,
      "notes": "负责 CI/CD 和系统监控"
    },
    {
      "agent_id": "clawcoordinator",
      "name": "ClawCoordinator",
      "role": "项目协调员",
      "status": "active",
      "workspace_path": "~/.openclaw/agents/clawcoordinator/workspace",
      "feishu_openid": "",
      "projects": [],
      "skills": ["project-management", "coordination"],
      "last_active": null,
      "notes": "负责项目规划和资源协调"
    },
    {
      "agent_id": "clawsupport",
      "name": "ClawSupport",
      "role": "运营支持官",
      "status": "active",
      "workspace_path": "~/.openclaw/agents/clawsupport/workspace",
      "feishu_openid": "",
      "projects": [],
      "skills": ["data-analysis", "reporting"],
      "last_active": null,
      "notes": "负责数据报表和财务追踪"
    },
    {
      "agent_id": "clawmarketer",
      "name": "ClawMarketer",
      "role": "市场增长官",
      "status": "active",
      "workspace_path": "~/.openclaw/agents/clawmarketer/workspace",
      "feishu_openid": "",
      "projects": [],
      "skills": ["content-creation", "growth-marketing"],
      "last_active": null,
      "notes": "负责品牌传播和用户增长"
    },
    {
      "agent_id": "marcus",
      "name": "Marcus",
      "role": "投资分析师",
      "status": "active",
      "workspace_path": "~/.openclaw/agents/marcus/workspace",
      "feishu_openid": "",
      "projects": [],
      "skills": ["stock-analysis", "portfolio-management"],
      "last_active": null,
      "notes": "负责股票分析和投资建议"
    }
  ]
}
EOF

echo -e "${GREEN}✓ 创建 Agent 注册表 registry.json${NC}"
echo ""

# ==========================================
# 步骤 5: 创建工具脚本
# ==========================================
echo "=========================================="
echo "  步骤 5: 创建工具脚本"
echo "=========================================="

# 创建 start-agent.sh
cat > "$WORKSPACE/scripts/start-agent.sh" << 'EOF'
#!/bin/bash
# 启动指定 Agent

AGENT_ID=$1
if [ -z "$AGENT_ID" ]; then
    echo "Usage: start-agent.sh <agent-id>"
    echo "Available agents: main, rex, clawbreaker, clawbuilder, clawguard, clawops, clawcoordinator, clawsupport, clawmarketer, marcus"
    exit 1
fi

AGENT_DIR="$HOME/.openclaw/agents/$AGENT_ID"
if [ ! -d "$AGENT_DIR" ]; then
    echo "Error: Agent not found: $AGENT_ID"
    exit 1
fi

# 加载 Agent 配置
export AGENT_SOUL="$AGENT_DIR/config/soul.md"
export AGENT_ROLE="$AGENT_DIR/config/role.md"
export AGENT_SKILLS="$AGENT_DIR/config/skills.json"
export AGENT_WORKSPACE="$AGENT_DIR/workspace"

echo "Starting agent: $AGENT_ID"
echo "Workspace: $AGENT_WORKSPACE"

# 启动 Agent session (需要根据实际 OpenClaw 命令调整)
# openclaw session start --agent "$AGENT_ID" --workspace "$AGENT_WORKSPACE"
EOF

chmod +x "$WORKSPACE/scripts/start-agent.sh"
echo -e "${GREEN}✓ 创建 start-agent.sh${NC}"

# 创建 list-agents.sh
cat > "$WORKSPACE/scripts/list-agents.sh" << 'EOF'
#!/bin/bash
# 列出所有已注册的 Agent

REGISTRY="$HOME/.openclaw/agents/registry.json"

if [ ! -f "$REGISTRY" ]; then
    echo "Error: Registry not found: $REGISTRY"
    exit 1
fi

echo "=========================================="
echo "  已注册的 Agent 列表"
echo "=========================================="
echo ""

# 使用 jq 解析 JSON (如果可用)
if command -v jq &> /dev/null; then
    jq -r '.agents[] | "\(.agent_id)\t\(.name)\t\(.role)\t\(.status)"' "$REGISTRY" | \
    column -t -s $'\t'
else
    # 简单输出
    echo "注意：安装 jq 可获得更好的显示效果"
    echo ""
    grep -E '"agent_id"|"name"|"role"|"status"' "$REGISTRY" | \
    sed 's/[",]//g' | \
    awk '{printf "%-15s", $2} NR%4==0{print ""}'
fi
EOF

chmod +x "$WORKSPACE/scripts/list-agents.sh"
echo -e "${GREEN}✓ 创建 list-agents.sh${NC}"

echo -e "${GREEN}✓ 工具脚本创建完成${NC}"
echo ""

# ==========================================
# 完成
# ==========================================
echo "=========================================="
echo "  初始化完成!"
echo "=========================================="
echo ""
echo -e "${GREEN}✓ Agent 独立工作区已创建${NC}"
echo -e "${GREEN}✓ 配置模板已就绪${NC}"
echo -e "${GREEN}✓ 共享数据目录已创建${NC}"
echo -e "${GREEN}✓ Agent 注册表已初始化${NC}"
echo -e "${GREEN}✓ 工具脚本已就绪${NC}"
echo ""
echo "下一步:"
echo "1. 在飞书中创建共享文档中心文件夹"
echo "2. 创建 Agent 注册多维表格"
echo "3. 创建任务管理多维表格"
echo "4. 为每个 Agent 生成具体配置"
echo ""
echo "相关文档:"
echo "- 架构设计：https://www.feishu.cn/docx/FjNJd4O3VoQxVox4tdOceMZKntk"
echo "- 实施清单：https://www.feishu.cn/docx/JA0FdJeeBoJAD8xWMjUcyusbndc"
echo ""

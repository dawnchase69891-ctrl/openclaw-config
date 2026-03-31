# 🔴 紧急问题清单 - 2026-03-23

> 基于系统审计发现的高优先级问题，按优先级排序

---

## P0 - 立即处理 (24 小时内)

### 1. API Key 暴露 🔴 严重

**问题**: API Key 在 14+ 个文件中明文存储

**影响**: 
- Git 提交可能意外泄露
- 任何有文件访问权限的用户都可获取
- 已提交到 GitHub 仓库

**修复步骤**:

```bash
# Step 1: 立即轮换密钥 (手动)
# 1. 阿里云控制台：https://dashscope.console.aliyun.com/apiKey
# 2. 飞书开放平台：https://open.feishu.cn/app

# Step 2: 创建安全的密钥存储
mkdir -p ~/.openclaw/workspace/.credentials
cat > ~/.openclaw/workspace/.env << 'EOF'
BAILIAN_API_KEY=sk-sp-新密钥
FEISHU_APP_ID=cli_a917e43cb0e29bc2
FEISHU_APP_SECRET=新密钥
EOF
chmod 600 ~/.openclaw/workspace/.env
chmod 600 ~/.openclaw/workspace/.credentials/*

# Step 3: 修改 openclaw.json 使用环境变量
# 将 "apiKey": "sk-sp-xxx" 改为 "apiKey": "${BAILIAN_API_KEY}"

# Step 4: 清理 git 历史
cd /home/uos/.openclaw/workspace
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .credentials/* .env' \
  --prune-empty --tag-name-filter cat -- --all

# Step 5: 强制推送
git push --force --all origin
git push --force --tags origin
```

**负责人**: CEO + ClawOps  
**截止时间**: 2026-03-24 20:00  
**状态**: ⏳ 待处理

---

### 2. 脚本硬编码密钥 🔴 严重

**问题**: 飞书密钥硬编码在 4 个脚本文件中

**受影响文件**:
- `scripts/task_check.py` (第 24-26 行)
- `scripts/daily_standup.py`
- `scripts/feishu_health_check.py`
- 其他 1 个文件

**修复步骤**:

```python
# 修改前 (❌)
FEISHU_APP_SECRET = "GfPZSnzF5cjlJsGcugIhSfHHi3HvAEHM"

# 修改后 (✅)
import os
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
env_file = WORKSPACE / '.env'

if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.startswith('FEISHU_APP_SECRET='):
                FEISHU_APP_SECRET = line.strip().split('=', 1)[1]
                break
else:
    FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
```

**批量修复命令**:
```bash
cd /home/uos/.openclaw/workspace
grep -r "GfPZSnzF5cjlJsGcugIhSfHHi3HvAEHM" scripts/ --include="*.py"
# 手动修改每个文件
```

**负责人**: ClawBuilder  
**截止时间**: 2026-03-24 20:00  
**状态**: ⏳ 待处理

---

## P1 - 本周内处理

### 3. Python 版本不匹配 🟡 中

**问题**: 系统 Python 3.7.3，脚本要求 >= 3.11

**影响**: 
- 诊断脚本报告版本警告
- 某些新特性无法使用

**修复步骤**:

```bash
# 检查可用的 Python 版本
which python3.11
python3.11 --version

# 修改 cron 任务使用正确的 Python 路径
crontab -e

# 将所有 python3 改为 python3.11 或完整路径
# 例如：/usr/bin/python3.11
```

**负责人**: ClawOps  
**截止时间**: 2026-03-28  
**状态**: ⏳ 待处理

---

### 4. 测试失败修复 🟡 中

**问题**: 81 个测试中 15 个失败/错误

**失败测试**:
- `test_collaboration_utils.py`: 6 个失败
- `test_config_sync.py`: 2 个失败
- `test_feishu_notifier.py`: 7 个 ERROR

**修复步骤**:

```bash
cd /home/uos/.openclaw/workspace

# 查看详细错误
python3 -m pytest tests/test_feishu_notifier.py -v --tb=long
python3 -m pytest tests/test_collaboration_utils.py -v --tb=long

# 修复后验证
python3 -m pytest tests/ -v
```

**负责人**: ClawGuard  
**截止时间**: 2026-03-28  
**状态**: ⏳ 待处理

---

### 5. GitHub Secrets 配置 🟡 中

**问题**: 无法验证 Secrets 是否正确配置

**需要配置的 Secrets**:
- [ ] `FEISHU_APP_ID`
- [ ] `FEISHU_APP_SECRET`
- [ ] `FEISHU_BITABLE_TOKEN`
- [ ] `BAILIAN_API_KEY`

**修复步骤**:

1. 访问：https://github.com/dawnchase69891-ctrl/openclaw-config/settings/secrets/actions
2. 添加上述 4 个 Secrets
3. 测试工作流：Actions → Sync Agent Config → Run workflow

**负责人**: ClawOps  
**截止时间**: 2026-03-26  
**状态**: ⏳ 待处理

---

### 6. 文件权限加固 🟡 中

**问题**: 敏感文件权限过宽 (644)

**修复步骤**:

```bash
cd /home/uos/.openclaw

# 限制配置文件权限
chmod 600 openclaw.json
chmod 600 agents/*/agent/models.json
chmod 600 workspace/.env
chmod 600 workspace/.credentials/*

# 验证
ls -la openclaw.json
ls -la agents/*/agent/models.json
```

**负责人**: ClawOps  
**截止时间**: 2026-03-26  
**状态**: ⏳ 待处理

---

## P2 - 下周处理

### 7. Git 仓库安全 🟢 低

**待办**:
- [ ] 启用 main 分支保护
- [ ] 配置 Required Reviews (至少 1 人)
- [ ] 启用 Commit Signing
- [ ] 配置 Status Checks

**负责人**: ClawOps  
**截止时间**: 2026-04-02

---

### 8. .gitignore 完善 🟢 低

**待办**:
- [ ] 添加 `*.log`
- [ ] 添加 `logs/`
- [ ] 添加 `.learnings/`
- [ ] 添加 `=3.*` (nvm 版本文件)

**负责人**: ClawBuilder  
**截止时间**: 2026-04-02

---

### 9. 飞书权限审计 🟢 低

**待办**:
- [ ] 登录飞书开放平台
- [ ] 检查应用权限列表
- [ ] 确认所有必需权限已开通
- [ ] 记录权限配置到文档

**负责人**: ClawCoordinator  
**截止时间**: 2026-04-02

---

### 10. 定期审计机制 🟢 低

**待办**:
- [ ] 创建每周审计 cron 任务
- [ ] 配置审计报告自动发送
- [ ] 建立问题跟踪流程
- [ ] 更新安全操作手册

**负责人**: ClawGuard  
**截止时间**: 2026-04-05

---

## 📊 跟踪表

| ID | 问题 | 优先级 | 负责人 | 截止 | 状态 |
|----|------|--------|--------|------|------|
| 1 | API Key 暴露 | P0 | CEO + ClawOps | 03-24 | ⏳ |
| 2 | 脚本硬编码密钥 | P0 | ClawBuilder | 03-24 | ⏳ |
| 3 | Python 版本 | P1 | ClawOps | 03-28 | ⏳ |
| 4 | 测试失败 | P1 | ClawGuard | 03-28 | ⏳ |
| 5 | GitHub Secrets | P1 | ClawOps | 03-26 | ⏳ |
| 6 | 文件权限 | P1 | ClawOps | 03-26 | ⏳ |
| 7 | Git 仓库安全 | P2 | ClawOps | 04-02 | ⏳ |
| 8 | .gitignore | P2 | ClawBuilder | 04-02 | ⏳ |
| 9 | 飞书权限 | P2 | ClawCoordinator | 04-02 | ⏳ |
| 10 | 定期审计 | P2 | ClawGuard | 04-05 | ⏳ |

---

**创建时间**: 2026-03-23 20:45  
**下次更新**: 每日站会前  
**跟踪文档**: `memory/issue-tracking.md`

# 独立 Agent 架构 - 部署指南

**版本**: v1.0  
**创建日期**: 2026-03-23  
**状态**: 🚀 准备部署

---

## 目录

1. [GitHub Secrets 配置](#一 github-secrets-配置)
2. [本地环境配置](#二本地环境配置)
3. [测试验证](#三测试验证)
4. [GitHub 仓库准备](#四 github-仓库准备)
5. [部署验证报告](#五部署验证报告)

---

## 一、GitHub Secrets 配置

### 1.1 必需 Secrets

在 GitHub 仓库设置中添加以下 Secrets：

**路径**: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

| Secret 名称 | 说明 | 示例值 | 来源 |
|------------|------|--------|------|
| `FEISHU_APP_ID` | 飞书应用 ID | `cli_a93bacddf1f89bd7` | 飞书开发者后台 |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | `ogM77ShlxBE6HcQ6Qn7uTbiJ1iGqGORS` | 飞书开发者后台 |
| `BITABLE_APP_TOKEN` | 多维表格 Token | `MxDxb1YyDair5XsO28Yc2WcknTe` | 飞书多维表格 URL |
| `BITABLE_TABLE_ID` | 表格 ID | `tblDKbuvCtBn3eew` | 飞书多维表格 URL |
| `FEISHU_WEBHOOK_URL` | 飞书 Webhook URL (可选) | `https://open.feishu.cn/open-apis/bot/v2/hook/xxx` | 飞书机器人 |

### 1.2 获取飞书凭证

#### Step 1: 获取 FEISHU_APP_ID 和 FEISHU_APP_SECRET

1. 访问 [飞书开发者后台](https://open.feishu.cn/app)
2. 选择或创建应用
3. 进入 `凭证与基础信息`
4. 复制 `App ID` 和 `App Secret`

#### Step 2: 获取 BITABLE_APP_TOKEN 和 BITABLE_TABLE_ID

1. 打开飞书多维表格
2. 从 URL 中提取：
   ```
   https://zquv5rbv5fk.feishu.cn/bitable/MxDxb1YyDair5XsO28Yc2WcknTe?table=tblDKbuvCtBn3eew
                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^      ^^^^^^^^^^^^^^^^
                                            BITABLE_APP_TOKEN                 BITABLE_TABLE_ID
   ```

#### Step 3: 获取 FEISHU_WEBHOOK_URL (可选)

1. 在飞书群中添加机器人
2. 复制 Webhook 地址

### 1.3 添加 Secrets

```bash
# 在 GitHub 仓库页面操作：
# 1. Settings → Secrets and variables → Actions
# 2. 点击 "New repository secret"
# 3. 依次添加上述 5 个 Secrets
```

---

## 二、本地环境配置

### 2.1 创建 .env 文件

在工作空间根目录创建 `.env` 文件：

```bash
cd ~/.openclaw/workspace
cat > .env << 'EOF'
# ===========================================
# 飞书 API 配置
# ===========================================

# 飞书应用凭证
FEISHU_APP_ID=cli_a93bacddf1f89bd7
FEISHU_APP_SECRET=ogM77ShlxBE6HcQ6Qn7uTbiJ1iGqGORS

# 多维表格配置
BITABLE_APP_TOKEN=MxDxb1YyDair5XsO28Yc2WcknTe
BITABLE_TABLE_ID=tblDKbuvCtBn3eew

# 飞书 Webhook (可选，用于通知)
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx

# ===========================================
# OpenClaw 配置
# ===========================================

# 默认接收人 (open_id)
DEFAULT_RECIPIENT=ou_9c111f465a69f41b26e059801d9b79f0

# 工作空间路径
WORKSPACE=/home/uos/.openclaw/workspace

# ===========================================
# 日志配置
# ===========================================

LOG_LEVEL=INFO
LOG_FORMAT=text
LOG_USE_UTC=false
EOF
```

### 2.2 环境变量说明

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `FEISHU_APP_ID` | ✅ | 飞书应用 ID |
| `FEISHU_APP_SECRET` | ✅ | 飞书应用密钥 |
| `BITABLE_APP_TOKEN` | ✅ | 多维表格 App Token |
| `BITABLE_TABLE_ID` | ✅ | 多维表格 Table ID |
| `FEISHU_WEBHOOK_URL` | ❌ | 飞书机器人 Webhook |
| `DEFAULT_RECIPIENT` | ❌ | 默认消息接收人 open_id |
| `WORKSPACE` | ❌ | 工作空间路径 |
| `LOG_LEVEL` | ❌ | 日志级别 (INFO/DEBUG/WARNING) |

### 2.3 .env 文件权限

```bash
# 设置 .env 文件权限为仅所有者可读写
chmod 600 ~/.openclaw/workspace/.env

# 验证权限
ls -la ~/.openclaw/workspace/.env
# 应该显示：-rw------- 1 uos uos ... .env
```

---

## 三、测试验证

### 3.1 运行诊断工具

```bash
cd ~/.openclaw/workspace
python3 scripts/diagnose.py
```

**预期输出**:
```
======================================================================
P2 模块诊断工具 v1.0
======================================================================

Python 版本：3.11.x
✅ Python 版本符合要求 (>= 3.11)

✅ pytest
✅ pytest-mock
✅ pytest-asyncio

✅ 依赖检查通过

脚本:
  ✅ scripts/feishu_doc_creator.py
  ✅ scripts/collaboration_utils.py
  ✅ scripts/task_queue_manager.py

模板:
  ✅ docs/templates/task-template.md
  ✅ docs/templates/decision-template.md
  ✅ docs/templates/meeting-template.md
  ✅ docs/templates/daily-report-template.md

测试:
  ✅ tests/conftest.py
  ✅ tests/test_integration.py

文档:
  ✅ docs/P2-API 文档.md
  ✅ docs/P2-部署指南.md
  ✅ docs/P2-故障排查指南.md

必要目录:
  ✅ .dead-letter/
  ✅ .backup/config
  ✅ docs/templates
  ✅ tests

OpenClaw 状态:
  ✅ 网关：运行中
  ✅ 会话：X 个

快速测试:
  ✅ 文档创建器：正常
  ✅ 协作工具：正常
  ✅ 任务队列：正常

======================================================================
诊断报告
======================================================================
时间：2026-03-23 18:30:00
工作空间：/home/uos/.openclaw/workspace

✅ Python 环境
✅ 依赖检查
✅ 文件结构
✅ 必要目录
✅ OpenClaw 状态
✅ 快速测试

总计：6/6 通过

🎉 所有检查通过！系统运行正常。
======================================================================
```

### 3.2 运行集成测试

```bash
cd ~/.openclaw/workspace
pytest tests/test_integration.py -v
```

**预期输出**:
```
============================= test session starts ==============================
platform linux -- Python 3.11.x, pytest-8.x.x, pluggy-1.x.x
rootdir: /home/uos/.openclaw/workspace
plugins: asyncio-0.x.x, mock-3.x.x

tests/test_integration.py::TestEndToEnd::test_config_sync_flow PASSED
tests/test_integration.py::TestEndToEnd::test_full_pipeline PASSED
tests/test_integration.py::TestFeishuNotification::test_send_message PASSED
tests/test_integration.py::TestFeishuNotification::test_send_with_retry PASSED
tests/test_integration.py::TestFeishuNotification::test_dead_letter_queue PASSED
tests/test_integration.py::TestPerformance::test_doc_creation_speed PASSED
tests/test_integration.py::TestPerformance::test_concurrent_creation PASSED
tests/test_integration.py::TestPerformance::test_resource_usage PASSED
tests/test_integration.py::TestTemplates::test_template_rendering PASSED
tests/test_integration.py::TestTemplates::test_variable_substitution PASSED
tests/test_integration.py::TestExceptions::test_missing_variable PASSED
tests/test_integration.py::TestExceptions::test_invalid_template PASSED

======================== 12 passed in 2.34s =============================
```

### 3.3 验证飞书通知

```bash
cd ~/.openclaw/workspace

# 方法 1: 使用 feishu_notifier.py
python3 scripts/feishu_notifier.py --test

# 方法 2: 使用 feishu_app_config.py
python3 feishu_app_config.py

# 方法 3: 手动测试
python3 -c "
from scripts.feishu_notifier import FeishuNotifier
notifier = FeishuNotifier()
notifier.send_text('【部署测试】骐骥助手已就绪 🐎')
print('✅ 飞书通知发送成功')
"
```

**预期输出**:
```
✅ 飞书通知发送成功
```

**验证步骤**:
1. 检查飞书是否收到测试消息
2. 消息发送者应为"骐骥助手"或应用名称
3. 消息内容应包含"【部署测试】"

### 3.4 验证配置同步

```bash
cd ~/.openclaw/workspace

# 测试配置验证脚本
python3 scripts/validate_config.py

# 测试飞书同步脚本
python3 scripts/sync_feishu_to_openclaw.py --dry-run
```

**预期输出**:
```
✅ 配置文件验证通过
✅ 飞书同步脚本正常
```

---

## 四、GitHub 仓库准备

### 4.1 检查 .gitignore

确保 `.gitignore` 包含以下内容：

```bash
cat > ~/.openclaw/workspace/.gitignore << 'EOF'
# 敏感信息
.env
.env.local
.env.*.local
.credentials/
*.pem
*.key

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/

# 日志
logs/
*.log

# 临时文件
.tmp/
tmp/
*.tmp
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db

# 死信队列
.dead-letter/

# 备份
.backup/
*.backup
*.bak

# 数据库
*.db
*.sqlite
*.sqlite3

# 测试
.pytest_cache/
.coverage
htmlcov/
.tox/

# OpenClaw
.message-queue/
.openclaw/
EOF
```

### 4.2 验证 .gitignore

```bash
cd ~/.openclaw/workspace

# 检查 .gitignore 是否生效
git check-ignore .env
git check-ignore .credentials/
git check-ignore logs/

# 应该输出对应的文件名，表示已被忽略
```

### 4.3 确认可以推送代码

```bash
cd ~/.openclaw/workspace

# 检查 Git 状态
git status

# 查看远程仓库
git remote -v

# 如果没有配置远程仓库，添加它
# git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 测试推送（不会真正推送）
git push --dry-run origin main
```

**预期输出**:
```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

### 4.4 提交部署文档

```bash
cd ~/.openclaw/workspace

# 添加部署文档
git add DEPLOYMENT.md .env.example

# 提交
git commit -m "docs: 添加部署指南和环境配置模板"

# 推送
git push origin main
```

---

## 五、部署验证报告

### 5.1 验证清单

| 验证项 | 检查内容 | 状态 | 备注 |
|--------|---------|------|------|
| GitHub Secrets | 5 个 Secrets 已配置 | ⬜ | 需用户确认 |
| .env 文件 | 已创建且权限正确 | ⬜ | 需执行 2.1 |
| 诊断工具 | 所有检查通过 | ⬜ | 需执行 3.1 |
| 集成测试 | 12 个测试全部通过 | ⬜ | 需执行 3.2 |
| 飞书通知 | 测试消息已收到 | ⬜ | 需执行 3.3 |
| 配置同步 | validate_config 通过 | ⬜ | 需执行 3.4 |
| .gitignore | 敏感文件已忽略 | ⬜ | 需执行 4.2 |
| Git 推送 | 可以正常推送 | ⬜ | 需执行 4.3 |

### 5.2 验证步骤

#### Step 1: 配置 GitHub Secrets (用户操作)

```
[ ] 访问 GitHub 仓库设置
[ ] 添加 FEISHU_APP_ID
[ ] 添加 FEISHU_APP_SECRET
[ ] 添加 BITABLE_APP_TOKEN
[ ] 添加 BITABLE_TABLE_ID
[ ] 添加 FEISHU_WEBHOOK_URL (可选)
```

#### Step 2: 创建本地环境配置

```bash
cd ~/.openclaw/workspace
cp .env.example .env
# 编辑 .env 填入实际凭证
chmod 600 .env
```

#### Step 3: 运行诊断和测试

```bash
# 诊断
python3 scripts/diagnose.py

# 测试
pytest tests/test_integration.py -v

# 飞书通知测试
python3 scripts/feishu_notifier.py --test
```

#### Step 4: 验证 Git 配置

```bash
git status
git remote -v
git push --dry-run origin main
```

### 5.3 问题排查

如果验证失败，参考以下文档：

- **部署问题**: `docs/P2-部署指南.md` → 第五章 常见问题
- **飞书集成**: `docs/P2-故障排查指南.md` → 第五章 飞书集成问题
- **测试失败**: `docs/P2-故障排查指南.md` → 第四章 运行问题

### 5.4 完成标准

所有验证项状态为 ✅ 时，部署完成。

---

## 六、后续步骤

### 6.1 配置 GitHub Actions

验证以下 Workflow 文件：

```bash
ls -la ~/.openclaw/workspace/.github/workflows/
# 应该看到：
# - sync-config.yml (配置同步)
```

### 6.2 设置定时任务

GitHub Actions 已配置每 5 分钟同步一次：

```yaml
on:
  schedule:
    - cron: '*/5 * * * *'  # 每 5 分钟
```

### 6.3 监控部署

- 查看 GitHub Actions 运行日志
- 监控飞书通知是否正常
- 定期检查配置同步状态

---

## 七、联系支持

如遇到问题：

1. 查看 `docs/P2-故障排查指南.md`
2. 检查 GitHub Actions 日志
3. 在飞书群提问

---

*文档版本：v1.0 | 维护者：clawops*

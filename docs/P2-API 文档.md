# P2 模块 API 文档

**版本**: v1.0  
**创建日期**: 2026-03-23  
**最后更新**: 2026-03-23

---

## 目录

1. [飞书文档创建器](#一飞书文档创建器)
2. [Agent 协作工具](#二 agent 协作工具)
3. [任务队列管理器](#三任务队列管理器)
4. [集成测试](#四集成测试)

---

## 一、飞书文档创建器

**模块**: `scripts/feishu_doc_creator.py`

### 1.1 功能概述

基于模板自动创建飞书文档，支持：
- 4 种文档模板（任务/决策/会议/日报）
- 变量替换系统（`{{variable}}` 语法）
- image[[...]] 占位符自动清理
- 自动归档到指定飞书文件夹

### 1.2 核心类

#### FeishuDocCreator

```python
from feishu_doc_creator import FeishuDocCreator

creator = FeishuDocCreator()
```

### 1.3 主要方法

#### create_from_template

从模板创建文档。

**参数**:
- `template` (str): 模板名称
  - `'task-template'`: 任务文档
  - `'decision-template'`: 决策记录
  - `'meeting-template'`: 会议纪要
  - `'daily-report-template'`: 日报
- `variables` (Dict, optional): 变量替换字典
- `folder_token` (str, optional): 目标文件夹 token
- `title` (str, optional): 文档标题
- `cleanup_images` (bool): 是否清理图片占位符，默认 True

**返回**:
```python
{
    'doc_id': 'DOC_20260323_180000',
    'title': '任务文档模板 - 2026-03-23',
    'template': 'task-template',
    'folder': 'UDARfZ30YlI7ild68FmcEoianSg',
    'content_preview': '...'
}
```

**示例**:
```python
doc_info = creator.create_from_template(
    template='task-template',
    variables={
        'task_id': 'TASK-20260323-001',
        'assignee': 'ClawBuilder',
        'deadline': '2026-03-25',
        'priority': 'P1',
        'description': '实现用户登录功能'
    },
    title='任务文档 - TASK-20260323-001'
)
```

#### list_templates

列出所有可用模板。

**返回**:
```python
[
    {
        'name': 'task-template',
        'description': '用于创建任务追踪文档',
        'file': 'task-template.md'
    },
    # ...
]
```

#### _replace_variables

替换模板变量（内部方法）。

**参数**:
- `content` (str): 模板内容
- `variables` (Dict): 变量字典

**返回**: 替换后的内容

#### _cleanup_image_placeholders

清理图片占位符（内部方法）。

**参数**:
- `content` (str): 文档内容

**返回**: 清理后的内容

### 1.4 模板变量

#### 任务文档模板 (task-template)

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{task_id}}` | 任务 ID | TASK-20260323-001 |
| `{{assignee}}` | 负责人 | ClawBuilder |
| `{{deadline}}` | 截止日期 | 2026-03-25 |
| `{{priority}}` | 优先级 | P0/P1/P2 |
| `{{description}}` | 任务描述 | 实现用户登录功能 |

#### 决策记录模板 (decision-template)

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{decision_id}}` | 决策 ID | DEC-20260323-001 |
| `{{decision_maker}}` | 决策人 | Jason |
| `{{participants}}` | 参与人 | Rex, ClawBreaker |
| `{{background}}` | 决策背景 | ... |
| `{{selected_option}}` | 选中选项 | 选项 A |

#### 会议纪要模板 (meeting-template)

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{meeting_date}}` | 会议日期 | 2026-03-23 |
| `{{topic}}` | 会议主题 | P2 模块评审会 |
| `{{meeting_time}}` | 会议时间 | 14:00-15:00 |
| `{{attendees}}` | 参会人员 | Jason, Rex |
| `{{recorder}}` | 记录人 | ClawBuilder |

#### 日报模板 (daily-report-template)

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{report_date}}` | 报告日期 | 2026-03-23 |
| `{{reporter}}` | 报告人 | ClawBuilder |

### 1.5 命令行使用

```bash
# 列出所有模板
python3 scripts/feishu_doc_creator.py list-templates

# 从模板创建文档
python3 scripts/feishu_doc_creator.py create task-template \
    task_id=TASK-001 \
    assignee=ClawBuilder \
    deadline=2026-03-25

# 显示模板内容
python3 scripts/feishu_doc_creator.py show-template task-template
```

---

## 二、Agent 协作工具

**模块**: `scripts/collaboration_utils.py`

### 2.1 功能概述

带可靠性保障的 sessions_send 封装：
- Agent 状态检查
- 指数退避重试机制
- 死信队列记录失败消息
- 异常分类处理

### 2.2 异常类

```python
from collaboration_utils import (
    CollaborationError,      # 协作异常基类
    AgentOfflineError,       # Agent 离线
    AgentBusyError,          # Agent 繁忙
    SessionSendError         # 发送失败
)
```

### 2.3 核心类

#### CollaborationService

```python
from collaboration_utils import CollaborationService

service = CollaborationService(
    dead_letter_path='/path/to/dead-letter'  # 可选
)
```

### 2.4 主要方法

#### send_with_retry

带重试的消息发送。

**参数**:
- `target` (str): 目标 Agent ID
- `message` (str): 消息内容
- `max_retries` (int): 最大重试次数，默认 3
- `check_status` (bool): 是否预先检查状态，默认 True
- `metadata` (Dict, optional): 附加元数据

**返回**: `bool` - 是否成功

**异常**:
- `AgentOfflineError`: Agent 离线
- `AgentBusyError`: Agent 繁忙
- `SessionSendError`: 发送失败

**示例**:
```python
try:
    success = await service.send_with_retry(
        target='clawbuilder',
        message='请实现用户登录功能',
        max_retries=3
    )
except AgentOfflineError as e:
    print(f"Agent 离线：{e}")
    # 记录死信队列
```

#### get_agent_status

获取 Agent 状态。

**参数**:
- `agent_id` (str): Agent ID

**返回**: `AgentStatus` 枚举
- `ONLINE`: 在线
- `BUSY`: 繁忙
- `OFFLINE`: 离线
- `UNKNOWN`: 未知

#### get_dead_letter_queue

获取死信队列。

**返回**: `List[DeadLetterMessage]`

#### retry_dead_letter

重试死信消息。

**参数**:
- `filepath` (str): 死信文件路径

**返回**: `bool` - 是否成功

### 2.5 便捷函数

```python
from collaboration_utils import (
    send_with_retry,      # 发送消息（带重试）
    check_agent_status,   # 检查 Agent 状态
    get_dead_letters      # 获取死信队列
)

# 使用示例
success = await send_with_retry('clawbuilder', '任务消息')
status = await check_agent_status('main')
dead_letters = await get_dead_letters()
```

### 2.6 命令行使用

```bash
# 检查 Agent 状态
python3 scripts/collaboration_utils.py check clawbuilder

# 发送消息（带重试）
python3 scripts/collaboration_utils.py send clawbuilder "请实现登录功能"

# 列出死信队列
python3 scripts/collaboration_utils.py list-dead-letters

# 重试死信消息
python3 scripts/collaboration_utils.py retry /path/to/dead_letter.json
```

---

## 三、任务队列管理器

**模块**: `scripts/task_queue_manager.py`

### 3.1 功能概述

带并发控制和超时监控的任务队列：
- 并发控制（max_concurrent）
- 任务超时
- 优先级队列
- 监控告警

### 3.2 核心类

#### TaskQueueManager

```python
from task_queue_manager import TaskQueueManager

manager = TaskQueueManager(
    max_concurrent=5,  # 最大并发数
    state_file='/path/to/state.json'  # 可选
)
```

### 3.3 主要方法

#### spawn_with_control

带并发控制的任务执行。

**参数**:
- `agent_id` (str): Agent ID
- `task` (str): 任务内容
- `priority` (int): 优先级 (1-10)，默认 1
- `timeout` (int): 超时时间 (秒)，默认 300

**返回**: 任务结果

**异常**:
- `asyncio.TimeoutError`: 任务超时
- `Exception`: 任务执行失败

**示例**:
```python
try:
    result = await manager.spawn_with_control(
        agent_id='clawbuilder',
        task='实现用户登录功能',
        priority=5,
        timeout=600
    )
except asyncio.TimeoutError:
    print("任务超时")
```

#### get_queue_status

获取队列状态。

**返回**:
```python
{
    'running': 2,
    'max_concurrent': 5,
    'queue_size': 3,
    'active_tasks': 2,
    'tasks': [...]
}
```

#### monitor_long_running_tasks

监控长时间运行的任务（后台任务）。

**示例**:
```python
await manager.monitor_long_running_tasks()
```

### 3.4 命令行使用

```bash
# 查看队列状态
python3 scripts/task_queue_manager.py status

# 提交任务
python3 scripts/task_queue_manager.py submit clawbuilder "实现登录功能"

# 启动监控
python3 scripts/task_queue_manager.py monitor
```

---

## 四、集成测试

**目录**: `tests/`

### 4.1 测试文件结构

```
tests/
├── conftest.py                 # pytest 配置
├── test_integration.py         # 集成测试
├── test_collaboration_utils.py # 协作工具测试（待完善）
└── test_task_queue.py          # 任务队列测试（待完善）
```

### 4.2 运行测试

```bash
# 安装依赖
pip install pytest pytest-mock pytest-asyncio

# 运行所有测试
cd ~/.openclaw/workspace
pytest tests/ -v

# 运行特定测试
pytest tests/test_integration.py -v

# 生成覆盖率报告
pytest tests/ --cov=scripts --cov-report=html
```

### 4.3 测试套件

#### EndToEnd 测试

- `test_config_sync_flow`: 配置同步流程
- `test_agent_communication_flow`: Agent 通信流程
- `test_task_execution_flow`: 任务执行流程
- `test_full_pipeline`: 完整流程测试

#### FeishuNotification 测试

- `test_doc_creation_notification`: 文档创建通知
- `test_variable_replacement`: 变量替换
- `test_image_cleanup`: 图片占位符清理

#### Performance 测试

- `test_doc_creation_performance`: 文档创建性能
- `test_variable_replacement_performance`: 变量替换性能
- `test_concurrent_doc_creation`: 并发文档创建

### 4.4 性能指标

| 测试项 | 目标 | 单位 |
|--------|------|------|
| 文档创建 | < 1.0 | 秒/文档 |
| 变量替换 | < 10 | 毫秒/次 |
| 并发创建 | < 1.0 | 秒/文档 (5 并发) |

---

## 五、文件夹 Token 参考

| 文件夹 | Token | 用途 |
|--------|-------|------|
| 公司事务/系统/ | `UDARfZ30YlI7ild68FmcEoianSg` | 系统配置、Agent 设置 |
| 公司事务/日报/ | `HV72frYGNlm3sVdE1vIcYSCHnac` | 公司日常运营日报 |
| 公司事务/会议/ | `Sfj4fDTgplB29xdGriSctLVHn4b` | 会议纪要 |
| 公司事务/决策/ | `UDARfZ30YlI7ild68FmcEoianSg` | 决策记录 |

---

## 六、错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| `ERR_TEMPLATE_NOT_FOUND` | 模板不存在 | 检查模板名称，确保模板文件存在 |
| `ERR_VARIABLE_MISSING` | 缺少必需变量 | 查看模板文档，提供所有必需变量 |
| `ERR_AGENT_OFFLINE` | Agent 离线 | 检查 Agent 状态，稍后重试 |
| `ERR_TASK_TIMEOUT` | 任务超时 | 增加 timeout 参数或优化任务 |
| `ERR_QUEUE_FULL` | 队列已满 | 等待任务完成或增加 max_concurrent |

---

## 七、最佳实践

### 7.1 文档创建

```python
# ✅ 推荐：提供完整变量
doc_info = creator.create_from_template(
    template='task-template',
    variables={
        'task_id': 'TASK-20260323-001',
        'assignee': 'ClawBuilder',
        'deadline': '2026-03-25',
        'priority': 'P1',
        'description': '实现用户登录功能'
    },
    title='任务文档 - TASK-20260323-001'
)

# ❌ 避免：缺少关键变量
doc_info = creator.create_from_template(
    template='task-template',
    variables={'task_id': 'TASK-001'}  # 缺少 assignee, deadline 等
)
```

### 7.2 Agent 通信

```python
# ✅ 推荐：捕获特定异常
try:
    success = await send_with_retry('clawbuilder', '任务', max_retries=3)
except AgentOfflineError:
    log_alert("Agent 离线")
except AgentBusyError:
    log_info("Agent 繁忙，稍后重试")

# ❌ 避免：不捕获异常
success = await send_with_retry('clawbuilder', '任务')  # 可能抛出异常
```

### 7.3 任务队列

```python
# ✅ 推荐：设置合理超时
await manager.spawn_with_control(
    agent_id='clawbuilder',
    task='复杂任务',
    timeout=600  # 10 分钟
)

# ❌ 避免：超时过短或过长
await manager.spawn_with_control(
    agent_id='clawbuilder',
    task='复杂任务',
    timeout=3600  # 1 小时太长
)
```

---

*文档版本：v1.0 | 维护者：clawbreaker*

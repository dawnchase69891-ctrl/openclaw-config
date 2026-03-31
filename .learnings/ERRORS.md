# Errors Log

错误和失败记录

---

## [ERR-20260311-001] feishu_stock_report.py 定时任务失败

**Logged**: 2026-03-11T11:35:00+08:00  
**Priority**: medium  
**Status**: resolved  
**Area**: config

### Summary
飞书股票日报脚本 (feishu_stock_report.py) 因缺少导入和字段映射错误导致 Cron 任务执行失败

### Error
```
Traceback (most recent call last):
  File "feishu_stock_report.py", line 142, in <module>
    content = generate_report()
  File "feishu_stock_report.py", line 82, in generate_report
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
NameError: name 'datetime' is not defined

Traceback (most recent call last):
  File "feishu_stock_report.py", line 139, in <module>
    content = generate_report()
  File "feishu_stock_report.py", line 105, in generate_report
    data = get_stock_data(stock['code'], stock['market'])
KeyError: 'market'

Traceback (most recent call last):
  File "feishu_stock_report.py", line 142, in <module>
    content = generate_report()
  File "feishu_stock_report.py", line 107, in generate_report
    profit_pct = ((data['current'] - stock['cost']) / stock['cost']) * 100
KeyError: 'cost'
```

### Context
- **触发时间**: 2026-03-11 10:00 (Cron 定时任务)
- **Cron 任务**: `飞书股票日报推送` (0 10 * * 1-5)
- **发现时间**: 11:30 (用户询问后才发现，延迟 90 分钟)
- **根本原因**:
  1. `portfolio_config.py` (03-10 创建) 是统一数据源，使用 `industry` 字段
  2. `feishu_stock_report.py` 未同步更新，仍使用 `sector` 字段
  3. 缺少必要的导入：`datetime`、`requests`
  4. 缺少字段映射：`market`、`cost` 未从配置导入
  5. 硬编码操作建议（含已清仓的森源电气）

### Suggested Fix
✅ **已修复**:
1. 添加 `import requests` 和 `from datetime import datetime`
2. 修正字段映射：`industry` → `sector`
3. 添加 `market` 字段（根据股票代码自动判断 sh/sz）
4. 添加 `cost` 字段（从 portfolio_config 导入）
5. 处理负数成本情况（做 T 成功）
6. 更新操作建议（移除森源电气）

🔲 **待改进**:
1. 添加脚本启动自检机制（导入/字段校验）
2. Cron 任务失败自动告警
3. 建立配置一致性检查工具
4. 发布前必须手动运行一次（已执行）

### Metadata
- **Reproducible**: yes
- **Related Files**: 
  - `~/.openclaw/workspace/scripts/feishu_stock_report.py`
  - `~/.openclaw/workspace/skills/a-stock-monitor/scripts/portfolio_config.py`
- **Related Cron**: `飞书股票日报推送` (9e28a4c0-7776-4523-be72-97cd062318da)
- **See Also**: MEMORY.md#2026-03-06---量化平台-web-发布质量教训 (同样的发布前测试缺失问题)

---

## 使用说明

**记录场景：**
- 命令返回非零退出码
- 异常或堆栈跟踪
- 意外输出或行为
- 超时或连接失败

**格式：**
```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
简要描述什么失败了

### Error
```
实际错误消息或输出
```

### Context
- 尝试的命令/操作
- 使用的输入或参数
- 相关的环境细节

### Suggested Fix
如果可以识别，什么可能解决这个问题

### Metadata
- Reproducible: yes | no | unknown
- Related Files: path/to/file.ext
- See Also: ERR-20250110-001 (如果重复出现)

---
```

---

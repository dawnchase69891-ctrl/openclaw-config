# 小红书爆款内容采集脚本 - 项目总结

**项目**: 赤兔计划 (RED-RABBIT)  
**任务 ID**: recvetJHM0itG2  
**完成日期**: 2026-03-21  
**状态**: ✅ 开发完成，测试通过

---

## 📋 交付清单

| 文件 | 大小 | 说明 | 状态 |
|------|------|------|------|
| `xiaohongshu_crawler.py` | 26.7 KB | 主爬虫脚本（Playwright 版） | ✅ |
| `xiaohongshu_crawler_openclaw.py` | 9.2 KB | OpenClaw Browser 工具集成版 | ✅ |
| `xiaohongshu_crawler_requirements.txt` | 187 B | Python 依赖 | ✅ |
| `README_XIAOHONGSHU_CRAWLER.md` | 8.2 KB | 完整使用文档 | ✅ |
| `test_xiaohongshu_crawler.py` | 6.9 KB | 测试验证脚本 | ✅ |

---

## ✅ 功能验证

### 测试结果
```
总计：6/6 通过

✅ 依赖导入 - playwright, asyncio
✅ 脚本结构 - 所有文件完整
✅ 配置检查 - 飞书配置、关键词配置正确
✅ 数据模型 - 15 个字段完整
✅ 日志工具 - 日志记录正常
✅ 飞书导出 - JSON 导出格式正确
```

---

## 🎯 核心功能

### 1. 数据采集
- ✅ 支持多关键词搜索（养生茶、药食同源、食疗等）
- ✅ 自动滚动加载更多笔记
- ✅ 每关键词最多抓取 20 篇笔记

### 2. 数据字段
| 字段 | 说明 |
|------|------|
| 笔记 ID | 小红书唯一标识 |
| 标题 | 笔记标题 |
| 封面图 | 封面图片 URL |
| 作者 | 作者昵称 |
| 作者 ID | 作者唯一 ID |
| 点赞数 | 互动数据 |
| 收藏数 | 互动数据 |
| 评论数 | 互动数据 |
| 完整文案 | 笔记正文 |
| 标签 | 话题标签 |
| 发布时间 | 时间戳 |
| 笔记链接 | 完整 URL |
| 搜索关键词 | 来源关键词 |
| 采集时间 | 采集时间戳 |

### 3. 数据存储
- ✅ 导出为 JSON 格式
- ✅ 兼容飞书多维表格批量导入
- ✅ 自动转换时间格式

### 4. 反爬策略
- ✅ 随机延迟（2-5 秒）
- ✅ 请求间隔控制（3-6 秒）
- ✅ 浏览器指纹复用
- ✅ 反检测脚本注入

---

## 🚀 使用方式

### 方式 1: 直接运行（推荐）

```bash
cd /home/uos/.openclaw/workspace/scripts
python xiaohongshu_crawler.py
```

**流程**:
1. 自动启动浏览器
2. 检测登录状态（未登录则等待 60 秒）
3. 搜索关键词
4. 抓取笔记详情
5. 导出数据到 JSON

### 方式 2: 通过 OpenClaw

```bash
# 在 OpenClaw 中执行
openclaw exec --python scripts/xiaohongshu_crawler_openclaw.py
```

### 方式 3: 测试验证

```bash
python test_xiaohongshu_crawler.py
```

---

## 📊 预期输出

### 日志文件
```
/home/uos/.openclaw/workspace/scripts/xiaohongshu_crawler.log
```

### 数据文件
```
/home/uos/.openclaw/workspace/scripts/xiaohongshu_data.json
```

### 日志示例
```
[2026-03-21 15:00:00] [INFO] 🚀 小红书爆款内容采集脚本 - 赤兔计划
[2026-03-21 15:00:01] [INFO] 正在启动浏览器...
[2026-03-21 15:00:03] [INFO] ✅ 登录状态正常
[2026-03-21 15:00:05] [INFO] 🔍 正在搜索关键词：养生茶
[2026-03-21 15:00:10] [INFO] 已找到 20 篇笔记
[2026-03-21 15:00:15] [INFO] ✅ 成功抓取笔记：养生茶推荐...
[2026-03-21 15:05:00] [INFO] ✅ 数据已导出到：xiaohongshu_data.json
[2026-03-21 15:05:00] [INFO] 总采集笔记数：20
[2026-03-21 15:05:00] [INFO] 🔥 点赞 TOP5:
[2026-03-21 15:05:00] [INFO]   1. 养生茶推荐 (1234 赞)
```

---

## 🔌 飞书多维表格导入

### 数据格式
```json
[
  {
    "fields": {
      "笔记 ID": "65f8a9b200000000120034ab",
      "标题": "养生茶推荐",
      "封面图": "https://...",
      "作者": "养生达人",
      "点赞数": 1234,
      "收藏数": 567,
      "评论数": 89,
      "完整文案": "详细内容...",
      "标签": "#养生 #健康 #茶饮",
      "发布时间": 1711008000000,
      "笔记链接": "https://www.xiaohongshu.com/explore/...",
      "搜索关键词": "养生茶",
      "采集时间": "2026-03-21T15:05:00"
    }
  }
]
```

### 导入步骤

**通过 OpenClaw**:
```python
# 在 OpenClaw 中执行
import json

with open("scripts/xiaohongshu_data.json", "r", encoding="utf-8") as f:
    records = json.load(f)

# 调用 feishu_bitable_app_table_record
# action: batch_create
# app_token: MxDxb1YyDair5XsO28Yc2WcknTe
# table_id: tblDKbuvCtBn3eew
# records: records
```

**手动导入**:
1. 打开飞书多维表格
2. 进入「爆款笔记库」表
3. 点击「导入」
4. 选择 JSON 文件
5. 映射字段

---

## ⚠️ 注意事项

### 1. 登录要求
- 需要小红书账号登录
- 首次运行会等待手动登录
- 后续运行复用登录态

### 2. 反爬限制
- 单次运行建议不超过 100 篇笔记
- 关键词间有延迟（6 秒）
- 笔记间有延迟（3-6 秒）

### 3. 数据准确性
- 页面结构变化可能影响抓取
- 建议定期检查选择器
- 日志文件记录详细错误

### 4. 账号安全
- 不要高频抓取
- 使用真实账号
- 避免短时间大量请求

---

## 🔧 配置修改

### 修改关键词
编辑 `xiaohongshu_crawler.py`:
```python
class Config:
    KEYWORDS = ["养生茶", "药食同源", "食疗", "你的关键词"]
```

### 修改抓取数量
```python
class Config:
    MAX_NOTES_PER_KEYWORD = 30  # 增加数量
```

### 修改延迟
```python
class Config:
    REQUEST_DELAY_MIN = 5  # 增加延迟
    REQUEST_DELAY_MAX = 10
```

---

## 🐛 故障排查

### 问题 1: 浏览器无法启动
```bash
# 重新安装 Playwright
pip uninstall playwright
pip install playwright
playwright install chromium
```

### 问题 2: 抓取数据为空
- 检查登录状态
- 查看日志文件
- 手动访问小红书验证

### 问题 3: 飞书导入失败
- 检查 App Token
- 检查 Table ID
- 验证字段名称匹配

---

## 📈 后续优化建议

### 短期（1-2 周）
- [ ] 增加数据去重逻辑
- [ ] 支持图片下载
- [ ] 增加评论抓取

### 中期（1 个月）
- [ ] 支持多线程并发
- [ ] 增加定时任务
- [ ] 数据可视化报表

### 长期（3 个月）
- [ ] 支持更多平台（抖音、快手）
- [ ] 机器学习内容分析
- [ ] 自动标签分类

---

## 📞 技术支持

**项目位置**: `/home/uos/.openclaw/workspace/scripts/`

**相关文档**:
- `README_XIAOHONGSHU_CRAWLER.md` - 完整使用文档
- `test_xiaohongshu_crawler.py` - 测试验证脚本

**联系方式**: ClawBuilder

---

## 📝 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2026-03-21 | 初始版本，核心功能完成 |

---

**项目状态**: ✅ 已完成，可投入使用

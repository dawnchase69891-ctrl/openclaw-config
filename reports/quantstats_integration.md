# 📊 quantstats 集成方案

**执行时间**: 2026-03-09 15:45  
**执行**: 骐骥 (Qíjì) 🐎  
**状态**: 🔄 进行中

---

## 🎯 集成目标

使用 **quantstats** 库增强金融 Agent 的报告能力：
- 专业的投资组合分析
- 丰富的可视化图表
- 详细的绩效指标
- HTML 交互式报告

---

## 📦 安装步骤

### 1. 安装依赖

```bash
pip3 install quantstats yfinance pandas numpy matplotlib
```

**预期输出**:
```
✅ quantstats 安装成功
✅ yfinance 安装成功
✅ pandas 安装成功
✅ numpy 安装成功
✅ matplotlib 安装成功
```

### 2. 验证安装

```python
import quantstats as qs
print(f"quantstats version: {qs.__version__}")
```

---

## 🔧 集成方案

### 方案 A: 独立报告脚本

创建 `quantstats_report.py`:

```python
#!/usr/bin/env python3
import quantstats as qs
import yfinance as yf
import pandas as pd
from datetime import datetime

# 持仓配置
STOCKS = {
    '恒逸石化': '000703.SZ',
    '汉缆股份': '002498.SZ',
    '中矿资源': '002738.SZ',
    '广电电气': '601616.SS',
    '中国卫通': '601698.SS',
}

# 下载数据
def fetch_portfolio_data():
    data = {}
    for name, ticker in STOCKS.items():
        df = yf.download(ticker, start='2025-01-01', progress=False)
        data[name] = df['Close'].pct_change()
    return data

# 生成报告
def generate_report():
    portfolio_data = fetch_portfolio_data()
    
    # 合并收益
    returns = pd.DataFrame(portfolio_data)
    
    # 生成 HTML 报告
    qs.reports.html(
        returns,
        title='持仓组合绩效报告',
        output='/home/uos/.openclaw/workspace/reports/quantstats_report.html'
    )
    
    print("✅ 报告生成成功")

if __name__ == '__main__':
    generate_report()
```

---

### 方案 B: 集成到现有金融 Agent

修改 `stock_report_generator.py`:

**新增功能**:
1. 在 PDF 报告后附加 quantstats HTML 报告链接
2. 增加绩效指标表格
3. 增加收益曲线图

**修改位置**:
- 第 200 行：添加 quantstats 导入
- 第 350 行：生成绩效指标
- 第 400 行：添加 HTML 报告链接

---

## 📊 报告内容示例

### 绩效指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 总收益率 | +XX.XX% | 成立以来总收益 |
| 年化收益率 | +XX.XX% | 年化复利 |
| 夏普比率 | X.XX | 风险调整后收益 |
| 最大回撤 | -XX.XX% | 最大亏损幅度 |
| 胜率 | XX.XX% | 盈利交易占比 |
| 盈亏比 | X.XX | 平均盈利/平均亏损 |

### 可视化图表

1. **收益曲线图** - 累计收益走势
2. **月度收益热力图** - 每月盈亏情况
3. **回撤分布图** - 风险暴露分析
4. **收益分布直方图** - 收益特征分析
5. **滚动波动率** - 风险变化趋势

---

## ⏰ 执行计划

### 第一阶段：安装 (今日)
- [x] 安装 quantstats 及依赖
- [ ] 验证安装成功
- [ ] 测试基础功能

### 第二阶段：集成 (明日)
- [ ] 创建独立报告脚本
- [ ] 测试数据获取
- [ ] 生成首份报告

### 第三阶段：优化 (本周)
- [ ] 集成到金融 Agent
- [ ] 添加定时任务
- [ ] 飞书推送报告链接

---

## 📁 文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| 报告脚本 | `scripts/quantstats_report.py` | 独立报告生成 |
| HTML 报告 | `reports/quantstats_report.html` | 交互式报告 |
| 配置文件 | `config.json` | 持仓配置 |

---

## ⚠️ 注意事项

1. **数据源**: 使用 yfinance 获取数据，可能需要代理
2. **A 股支持**: A 股代码格式 `000703.SZ` / `601616.SS`
3. **报告大小**: HTML 报告约 1-2MB，包含图表
4. **生成时间**: 首次生成约 30-60 秒

---

## 🚀 预期效果

### 当前报告 (v3.0)
- 文字描述为主
- 简单表格
- PDF 格式

### 增强后报告
- 交互式 HTML
- 丰富图表
- 专业绩效指标
- 可筛选时间范围
- 可导出多种格式

---

**下一步**: 等待安装完成 → 创建测试脚本 → 生成首份报告

**执行人**: 骐骥 (Qíjì) 🐎

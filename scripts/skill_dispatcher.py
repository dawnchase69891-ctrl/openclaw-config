#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill 智能调度脚本

用途：根据任务自动选择最优 Skill 组合
使用：python3 skill_dispatcher.py <任务描述>

原则：
1. 专业人干专业事
2. 优先使用已有 Skill
3. 多 Skill 协同验证
4. 最优解优先
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

# 配置
WORKSPACE = Path('/home/uos/.openclaw/workspace')
SKILLS_DIR = WORKSPACE / 'skills'
FEISHU_SKILLS_DIR = WORKSPACE.parent / 'extensions' / 'openclaw-lark' / 'skills'

# Skill 分类数据库
SKILL_DATABASE = {
    '金融投资': {
        'a-stock-monitor': {
            'keywords': ['A 股', '股票推荐', '市场情绪', '量化监控', '选股'],
            'priority': 5,
            'auto': True,
            'collaboration': ['finnhub-pro', 'tushare-finance', 'dashboard']
        },
        'finnhub-pro': {
            'keywords': ['美股', '股价', '财报', '内部人交易', '分析师'],
            'priority': 4,
            'auto': False,
            'collaboration': ['us-stock-analysis', 'yahoo-finance']
        },
        'backtest-expert': {
            'keywords': ['回测', '策略验证', '参数优化', '过拟合'],
            'priority': 4,
            'auto': False,
            'collaboration': ['dashboard', 'data-analysis']
        },
        'trading': {
            'keywords': ['技术分析', '图表模式', '风险管理', '仓位'],
            'priority': 4,
            'auto': False,
            'collaboration': ['financial-calculator', 'backtest-expert']
        },
        'financial-agent-core': {
            'keywords': ['投资建议', '投资组合', '资产配置', 'Marcus'],
            'priority': 5,
            'auto': False,
            'collaboration': ['*']  # 可调度所有金融 Skill
        },
        'stock-analysis': {
            'keywords': ['股票分析', '基本面', '技术面', '对比'],
            'priority': 4,
            'auto': False,
            'collaboration': ['yahoo-finance', 'finnhub-pro']
        },
        'trading-coach': {
            'keywords': ['交易复盘', '交易 CSV', '盈亏统计', '交易分析'],
            'priority': 4,
            'auto': False,
            'collaboration': ['data-analysis']
        },
        'tushare-finance': {
            'keywords': ['宏观数据', 'GDP', 'CPI', 'A 股数据', '港股'],
            'priority': 4,
            'auto': False,
            'collaboration': ['a-stock-monitor', 'dashboard']
        },
        'financial-calculator': {
            'keywords': ['复利', '现值', '终值', '定价', '计算'],
            'priority': 4,
            'auto': False,
            'collaboration': []
        },
        'us-stock-analysis': {
            'keywords': ['美股分析', 'AAPL', 'TSLA', 'NVDA'],
            'priority': 4,
            'auto': False,
            'collaboration': ['finnhub-pro', 'yahoo-finance']
        },
        'yahoo-finance': {
            'keywords': ['Yahoo', '股息', '期权', '财报'],
            'priority': 4,
            'auto': False,
            'collaboration': ['stock-analysis']
        },
        'day-trading-skill': {
            'keywords': ['日内交易', '价格行为', '短线'],
            'priority': 3,
            'auto': False,
            'collaboration': ['trading']
        },
        'stock-info-explorer': {
            'keywords': ['股票报告', 'K 线图', '基本面摘要'],
            'priority': 4,
            'auto': False,
            'collaboration': ['yahoo-finance']
        },
        'cfo': {
            'keywords': ['财务规划', '现金流', '融资', '资本分配'],
            'priority': 3,
            'auto': False,
            'collaboration': ['financial-calculator']
        },
        'economic-calendar-fetcher': {
            'keywords': ['经济日历', '财报季', '央行会议'],
            'priority': 3,
            'auto': True,
            'collaboration': ['market-environment-analysis']
        }
    },
    '飞书集成': {
        'feishu-bitable': {
            'keywords': ['多维表格', 'bitable', '数据表', '记录', '字段'],
            'priority': 5,
            'auto': False,
            'collaboration': ['feishu-drive']
        },
        'feishu-calendar': {
            'keywords': ['日程', '会议', '日历', '约会议', '忙闲'],
            'priority': 5,
            'auto': True,
            'collaboration': ['feishu-task', 'feishu-im-user-message']
        },
        'feishu-task': {
            'keywords': ['任务', '待办', 'to-do', '清单'],
            'priority': 5,
            'auto': False,
            'collaboration': ['feishu-calendar']
        },
        'feishu-doc-manager': {
            'keywords': ['飞书文档', '发布文档', '云文档'],
            'priority': 4,
            'auto': False,
            'collaboration': ['feishu-drive']
        },
        'feishu-drive': {
            'keywords': ['云空间', '云盘', '文件', '上传', '下载'],
            'priority': 3,
            'auto': False,
            'collaboration': []
        },
        'feishu-calendar-event': {
            'keywords': ['创建会议', '修改日程', '删除日程'],
            'priority': 5,
            'auto': False,
            'collaboration': ['feishu-calendar']
        },
        'feishu-im-user-message': {
            'keywords': ['发消息', '飞书消息', '通知'],
            'priority': 4,
            'auto': False,
            'collaboration': []
        },
        'feishu-search-user': {
            'keywords': ['搜索用户', '找同事', '员工信息'],
            'priority': 3,
            'auto': False,
            'collaboration': []
        },
        'feishu': {
            'keywords': ['飞书', '群聊', '群成员'],
            'priority': 5,
            'auto': False,
            'collaboration': ['*']
        }
    },
    '数据分析': {
        'data-analysis': {
            'keywords': ['数据分析', '统计', '数据解读', '决策'],
            'priority': 5,
            'auto': False,
            'collaboration': ['dashboard']
        },
        'dashboard': {
            'keywords': ['看板', '可视化', '图表', 'dashboard'],
            'priority': 5,
            'auto': False,
            'collaboration': ['data-analysis']
        },
        'market-analysis-cn': {
            'keywords': ['市场分析', '竞品分析', '趋势', '用户行为'],
            'priority': 4,
            'auto': False,
            'collaboration': ['market-environment-analysis']
        },
        'market-environment-analysis': {
            'keywords': ['市场环境', '全球市场', '相場環境', '風險偏好'],
            'priority': 5,
            'auto': True,
            'collaboration': ['market-analysis-cn', 'economic-calendar-fetcher']
        }
    },
    '角色技能': {
        'clawsquad': {
            'keywords': ['ClawSquad', '产研团队', '需求评审', '产品开发'],
            'priority': 5,
            'auto': False,
            'collaboration': ['agency-agents-openclaw']
        },
        'clawmarketer': {
            'keywords': ['营销', '推广', '内容创作', '社群运营'],
            'priority': 4,
            'auto': False,
            'collaboration': []
        },
        'clawcoordinator': {
            'keywords': ['项目协调', '流程', '进度', '变更管理'],
            'priority': 5,
            'auto': False,
            'collaboration': ['change_gate.py']
        },
        'clawsupport': {
            'keywords': ['运营', '客服', '报表', '财务追踪', '合规'],
            'priority': 4,
            'auto': False,
            'collaboration': ['feishu-bitable', 'config_monitor.py']
        },
        'agency-agents-openclaw': {
            'keywords': ['Agent', '编排', '部门协作', '多 Agent'],
            'priority': 5,
            'auto': False,
            'collaboration': ['clawsquad']
        }
    },
    '工具效率': {
        'find-skills': {
            'keywords': ['skill', '安装', '搜索', '发现'],
            'priority': 4,
            'auto': False,
            'collaboration': ['skillhub', 'clawhub']
        },
        'agent-browser': {
            'keywords': ['浏览器', '网页', '截图', '自动化'],
            'priority': 4,
            'auto': False,
            'collaboration': []
        },
        'healthcheck': {
            'keywords': ['安全检查', '加固', '审计', '风险'],
            'priority': 3,
            'auto': True,
            'collaboration': []
        },
        'self-improvement': {
            'keywords': ['学习', '改进', '错误', '经验'],
            'priority': 5,
            'auto': True,
            'collaboration': []
        },
        'gog': {
            'keywords': ['Google', 'Gmail', 'Google 日历', 'Google Drive'],
            'priority': 3,
            'auto': False,
            'collaboration': []
        }
    }
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def match_skill(task, skill_info):
    """匹配 Skill"""
    score = 0
    matched_keywords = []
    
    for keyword in skill_info['keywords']:
        if keyword.lower() in task.lower():
            score += 1
            matched_keywords.append(keyword)
    
    return score, matched_keywords

def find_best_skills(task):
    """查找最适合的 Skill"""
    results = []
    
    for category, skills in SKILL_DATABASE.items():
        for skill_name, skill_info in skills.items():
            score, matched = match_skill(task, skill_info)
            if score > 0:
                results.append({
                    'category': category,
                    'skill': skill_name,
                    'score': score,
                    'priority': skill_info['priority'],
                    'matched_keywords': matched,
                    'auto': skill_info['auto'],
                    'collaboration': skill_info['collaboration']
                })
    
    # 排序：分数 > 优先级 > 类别
    results.sort(key=lambda x: (-x['score'], -x['priority'], x['category']))
    
    return results

def generate_skill_plan(task, results):
    """生成 Skill 执行计划"""
    if not results:
        return None
    
    # 选择最佳 Skill
    best = results[0]
    
    plan = {
        'primary': best,
        'collaboration': [],
        'verification': [],
        'fallback': []
    }
    
    # 添加协同 Skill
    for collab in best['collaboration']:
        if collab != '*':
            for r in results:
                if r['skill'] == collab:
                    plan['collaboration'].append(r)
                    break
    
    # 添加验证 Skill (同任务不同实现)
    if best['score'] >= 2:
        for r in results[1:3]:
            if r['category'] == best['category'] and r['skill'] != best['skill']:
                plan['verification'].append(r)
    
    # 添加备选 Skill
    if len(results) > 3:
        plan['fallback'] = results[3:5]
    
    return plan

def print_plan(plan, task):
    """打印执行计划"""
    print_header("Skill 智能调度方案")
    
    print_info(f"任务：{task}")
    print()
    
    # 主 Skill
    primary = plan['primary']
    print(f"{Colors.BOLD}🎯 主执行 Skill:{Colors.END}")
    print(f"  类别：{primary['category']}")
    print(f"  Skill: {primary['skill']}")
    print(f"  匹配度：{primary['score']} 关键词")
    print(f"  优先级：{'⭐'*primary['priority']}")
    print(f"  匹配词：{', '.join(primary['matched_keywords'])}")
    print(f"  自动化：{'✅' if primary['auto'] else '❌'}")
    print()
    
    # 协同 Skill
    if plan['collaboration']:
        print(f"{Colors.BOLD}🤝 协同 Skill:{Colors.END}")
        for collab in plan['collaboration']:
            print(f"  - {collab['skill']} ({collab['category']})")
        print()
    
    # 验证 Skill
    if plan['verification']:
        print(f"{Colors.BOLD}✅ 验证 Skill:{Colors.END}")
        for verify in plan['verification']:
            print(f"  - {verify['skill']} ({verify['category']})")
        print()
    
    # 备选 Skill
    if plan['fallback']:
        print(f"{Colors.BOLD}🔄 备选 Skill:{Colors.END}")
        for fallback in plan['fallback']:
            print(f"  - {fallback['skill']} ({fallback['category']})")
        print()
    
    # 执行建议
    print(f"{Colors.BOLD}💡 执行建议:{Colors.END}")
    if primary['auto']:
        print_success("此任务可自动化执行")
    else:
        print_info("此任务需人工确认执行")
    
    if plan['verification']:
        print_info("建议多 Skill 协同验证结果")
    
    print()

def main():
    if len(sys.argv) < 2:
        print_header("Skill 智能调度系统")
        print_info("用法：python3 skill_dispatcher.py <任务描述>")
        print_info("示例：python3 skill_dispatcher.py '分析今天 A 股市场'")
        sys.exit(1)
    
    task = ' '.join(sys.argv[1:])
    
    print_header("Skill 智能调度系统")
    print_info(f"分析任务：{task}")
    print_info(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 查找最佳 Skill
    results = find_best_skills(task)
    
    if not results:
        print_error("未找到匹配的 Skill")
        print_info("建议：使用 find-skills 搜索相关 Skill")
        sys.exit(1)
    
    # 生成执行计划
    plan = generate_skill_plan(task, results)
    
    # 打印计划
    print_plan(plan, task)
    
    # 保存计划
    plan_file = WORKSPACE / '.skill_plans' / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    plan_file.parent.mkdir(exist_ok=True)
    
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump({
            'task': task,
            'timestamp': datetime.now().isoformat(),
            'plan': plan,
            'all_results': results
        }, f, ensure_ascii=False, indent=2)
    
    print_success(f"执行计划已保存：{plan_file}")

if __name__ == '__main__':
    main()

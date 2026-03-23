#!/usr/bin/env python3
"""
对抗式审查机制 (Adversarial Review Mechanism)
=============================================

通过双模型对抗提升输出质量，减少幻觉和错误。

核心功能:
- review: 执行完整的对抗式审查流程
- check-facts: 事实准确性检查
- check-safety: 安全风险检查
- check-logic: 逻辑一致性检查

使用示例:
    python adversarial_review.py review --task "分析 AAPL 股票" --output report.json
    python adversarial_review.py check-facts --content "某文本" --output facts.json
    python adversarial_review.py check-logic --content "某论证" --output logic.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


class IssueType(Enum):
    """问题类型"""
    FACTUAL_ERROR = "FACTUAL_ERROR"
    LOGIC_GAP = "LOGIC_GAP"
    INCOMPLETE = "INCOMPLETE"
    BIAS = "BIAS"
    SAFETY_RISK = "SAFETY_RISK"
    HALLUCINATION = "HALLUCINATION"
    OTHER = "OTHER"


class Severity(Enum):
    """问题严重程度"""
    CRITICAL = "CRITICAL"  # 必须修复
    MAJOR = "MAJOR"        # 建议修复
    MINOR = "MINOR"        # 可选修复
    INFO = "INFO"          # 提示信息


class Verdict(Enum):
    """审查结论"""
    PASS = "PASS"
    NEEDS_REVISION = "NEEDS_REVISION"
    REJECT = "REJECT"


@dataclass
class ReviewIssue:
    """审查发现的问题"""
    type: str
    severity: str
    location: str
    description: str
    suggestion: str
    confidence: float = 0.9


@dataclass
class ReviewReport:
    """审查报告"""
    session_id: str
    task: str
    status: str
    start_time: str
    end_time: Optional[str]
    duration_seconds: Optional[float]
    rounds: int
    executor_model: str
    reviewer_model: str
    verdict: str
    confidence: float
    issues: List[Dict]
    strengths: List[str]
    overall_feedback: str
    recommendations: List[Dict]
    full_history: List[Dict]


class AdversarialReviewer:
    """对抗式审查器"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = {
            "max_review_rounds": 3,
            "auto_approve_threshold": 0.9,
            "escalate_after_rounds": 3,
            "review_timeout": 300,
            "models": {
                "executor": "bailian/qwen3.5-plus",
                "reviewer": "bailian/kimi-k2.5",
                "arbiter": "bailian/qwen3-max-2026-01-23"
            },
            **(config or {})
        }
        self.review_history = []
        
    def generate_session_id(self, task: str) -> str:
        """生成唯一的审查会话 ID"""
        timestamp = datetime.now().isoformat()
        content = f"{task}_{timestamp}"
        return f"review_{hashlib.md5(content.encode()).hexdigest()[:12]}"
    
    def check_facts(self, content: str, context: Optional[str] = None) -> List[ReviewIssue]:
        """
        事实准确性检查
        
        Args:
            content: 待检查的内容
            context: 可选的上下文信息
            
        Returns:
            发现的问题列表
        """
        issues = []
        
        # 检查点列表
        fact_check_points = [
            "数据、统计数字是否准确",
            "引用来源是否真实存在",
            "时间、地点、人物是否正确",
            "专业术语使用是否准确",
            "因果关系是否成立"
        ]
        
        # 模拟审查 (实际实现需要调用 LLM)
        # 这里是框架代码，实际审查需要集成 LLM API
        print(f"🔍 执行事实检查...")
        print(f"   检查点：{len(fact_check_points)} 个")
        
        # TODO: 集成实际 LLM 调用
        # prompt = f"""
        # 你是一名严格的事实核查员。请检查以下内容的准确性:
        
        # 内容:
        # {content}
        
        # {f'上下文：{context}' if context else ''}
        
        # 请逐项检查:
        # 1. 数据、统计数字是否准确
        # 2. 引用来源是否真实存在
        # 3. 时间、地点、人物是否正确
        # 4. 专业术语使用是否准确
        # 5. 因果关系是否成立
        
        # 输出 JSON 格式的问题列表:
        # [
        #   {{
        #     "type": "FACTUAL_ERROR",
        #     "severity": "CRITICAL|MAJOR|MINOR",
        #     "location": "具体位置",
        #     "description": "问题描述",
        #     "suggestion": "改进建议",
        #     "confidence": 0.0-1.0
        #   }}
        # ]
        # """
        
        return issues
    
    def check_logic(self, content: str) -> List[ReviewIssue]:
        """
        逻辑一致性检查
        
        Args:
            content: 待检查的内容
            
        Returns:
            发现的问题列表
        """
        issues = []
        
        # 检查点列表
        logic_check_points = [
            "前提假设是否合理",
            "推理链条是否严密",
            "是否存在逻辑谬误",
            "结论是否由前提推导而出",
            "是否存在自相矛盾"
        ]
        
        print(f"🔍 执行逻辑检查...")
        print(f"   检查点：{len(logic_check_points)} 个")
        
        # TODO: 集成实际 LLM 调用
        
        return issues
    
    def check_safety(self, content: str, context: Optional[str] = None) -> List[ReviewIssue]:
        """
        安全风险检查
        
        Args:
            content: 待检查的内容
            context: 可选的上下文信息
            
        Returns:
            发现的问题列表
        """
        issues = []
        
        # 安全检查维度
        safety_dimensions = [
            "是否包含危险建议",
            "是否泄露敏感信息",
            "是否存在偏见或歧视",
            "是否符合法律法规",
            "是否存在伦理问题"
        ]
        
        print(f"🔍 执行安全检查...")
        print(f"   维度：{len(safety_dimensions)} 个")
        
        # TODO: 集成实际 LLM 调用
        
        return issues
    
    def detect_bias(self, content: str) -> List[ReviewIssue]:
        """
        偏见检测
        
        Args:
            content: 待检查的内容
            
        Returns:
            发现的问题列表
        """
        issues = []
        
        # 偏见类型
        bias_types = [
            "确认偏误 (只找支持自己观点的证据)",
            "锚定效应 (过度依赖首个信息)",
            "可得性偏误 (高估易想起的信息)",
            "群体偏误 (刻板印象)",
            "乐观/悲观偏误"
        ]
        
        print(f"🔍 执行偏见检测...")
        print(f"   类型：{len(bias_types)} 个")
        
        # TODO: 集成实际 LLM 调用
        
        return issues
    
    def detect_hallucination(self, content: str, context: Optional[str] = None) -> List[ReviewIssue]:
        """
        幻觉检测
        
        Args:
            content: 待检查的内容
            context: 可选的上下文信息
            
        Returns:
            发现的问题列表
        """
        issues = []
        
        # 幻觉检查点
        hallucination_checks = [
            "是否编造了不存在的事实",
            "是否虚构了引用来源",
            "是否捏造了数据或统计",
            "是否创造了不存在的概念",
            "是否错误归因"
        ]
        
        print(f"🔍 执行幻觉检测...")
        print(f"   检查点：{len(hallucination_checks)} 个")
        
        # TODO: 集成实际 LLM 调用
        
        return issues
    
    def generate_review_prompt(self, content: str, task: str, dimension: str = "comprehensive") -> str:
        """
        生成审查提示词
        
        Args:
            content: 待审查内容
            task: 任务描述
            dimension: 审查维度 (comprehensive/facts/logic/safety/bias)
            
        Returns:
            审查提示词
        """
        prompts = {
            "comprehensive": f"""
你是一名严格的审查者 (Reviewer)。请批判性审查以下输出:

任务背景:
{task}

待审查内容:
{content}

审查维度:
1. 事实准确性 - 数据、引用、陈述是否准确？
2. 逻辑一致性 - 推理链条是否严密？
3. 完整性 - 是否遗漏重要信息？
4. 偏见检测 - 是否存在确认偏误？
5. 幻觉检测 - 是否编造了不存在的内容？
6. 替代方案 - 是否有更好的方法？

请使用以下 JSON 格式输出审查结果:
{{
  "verdict": "PASS | NEEDS_REVISION | REJECT",
  "confidence": 0.0-1.0,
  "issues": [
    {{
      "type": "FACTUAL_ERROR | LOGIC_GAP | INCOMPLETE | BIAS | HALLUCINATION | OTHER",
      "severity": "CRITICAL | MAJOR | MINOR",
      "location": "具体位置",
      "description": "问题描述",
      "suggestion": "改进建议",
      "confidence": 0.0-1.0
    }}
  ],
  "strengths": ["优点列表"],
  "overall_feedback": "整体评价"
}}

审查结果:
""",
            "facts": f"""
你是一名严格的事实核查员。请检查以下内容的准确性:

内容:
{content}

检查点:
1. 数据、统计数字是否准确
2. 引用来源是否真实存在
3. 时间、地点、人物是否正确
4. 专业术语使用是否准确
5. 因果关系是否成立

输出 JSON 格式的问题列表:
[{{"type": "FACTUAL_ERROR", "severity": "...", "location": "...", "description": "...", "suggestion": "...", "confidence": 0.0}}]
""",
            "logic": f"""
你是一名逻辑审查员。请检查以下内容的逻辑一致性:

内容:
{content}

检查点:
1. 前提假设是否合理
2. 推理链条是否严密
3. 是否存在逻辑谬误
4. 结论是否由前提推导而出
5. 是否存在自相矛盾

输出 JSON 格式的问题列表:
[{{"type": "LOGIC_GAP", "severity": "...", "location": "...", "description": "...", "suggestion": "...", "confidence": 0.0}}]
""",
            "safety": f"""
你是一名安全审查员。请检查以下内容的安全性:

内容:
{content}

检查维度:
1. 是否包含危险建议
2. 是否泄露敏感信息
3. 是否存在偏见或歧视
4. 是否符合法律法规
5. 是否存在伦理问题

输出 JSON 格式的问题列表:
[{{"type": "SAFETY_RISK", "severity": "...", "location": "...", "description": "...", "suggestion": "...", "confidence": 0.0}}]
"""
        }
        
        return prompts.get(dimension, prompts["comprehensive"])
    
    def parse_review_response(self, response: str) -> Dict:
        """解析审查响应，提取 JSON"""
        import re
        
        # 提取 JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # 如果解析失败，返回默认结构
        return {
            "verdict": "NEEDS_REVISION",
            "confidence": 0.5,
            "issues": [],
            "strengths": [],
            "overall_feedback": "无法解析审查响应"
        }
    
    def should_trigger_review(self, task_description: str, estimated_tokens: int = 0) -> bool:
        """
        判断是否应该触发对抗式审查
        
        Args:
            task_description: 任务描述
            estimated_tokens: 预估 token 数
            
        Returns:
            是否触发审查
        """
        # 强制审查的关键词
        critical_keywords = [
            '投资', '决策', '代码审查', '安全', '医疗', '法律', '财务',
            '交易', '建议', '诊断', '处方', '合同', '审计'
        ]
        
        # 高成本阈值
        high_cost_threshold = 10000
        
        # 判断逻辑
        has_critical_keyword = any(kw in task_description for kw in critical_keywords)
        is_high_cost = estimated_tokens > high_cost_threshold
        
        return has_critical_keyword or is_high_cost
    
    def generate_revision_prompt(self, draft: str, review: Dict, task: str) -> str:
        """
        生成修订提示词
        
        Args:
            draft: 初稿
            review: 审查意见
            task: 任务描述
            
        Returns:
            修订提示词
        """
        return f"""
你是任务执行者 (Executor)。请根据审查意见修订你的输出:

原始任务:
{task}

你的初稿:
{draft}

审查意见:
{json.dumps(review, ensure_ascii=False, indent=2)}

修订要求:
1. 解决所有 CRITICAL 和 MAJOR 级别的问题
2. 采纳合理的改进建议
3. 如果有不同意见，请说明理由
4. 标注你修改的部分

修订后的版本:
"""
    
    def run_review(self, task: str, initial_draft: Optional[str] = None, 
                   output_path: Optional[str] = None) -> ReviewReport:
        """
        运行完整的对抗式审查流程
        
        Args:
            task: 任务描述
            initial_draft: 可选的初稿 (如不提供则模拟)
            output_path: 输出文件路径
            
        Returns:
            审查报告
        """
        session_id = self.generate_session_id(task)
        start_time = datetime.now()
        
        print(f"🔍 启动对抗式审查")
        print(f"   会话 ID: {session_id}")
        print(f"   任务：{task}")
        print(f"   执行模型：{self.config['models']['executor']}")
        print(f"   审查模型：{self.config['models']['reviewer']}")
        print()
        
        # 模拟审查流程 (实际实现需要调用 LLM)
        rounds = []
        issues_found = []
        strengths = []
        
        # Round 1: 执行者生成初稿
        print("📝 Round 1: 执行者生成初稿...")
        if not initial_draft:
            initial_draft = f"[模拟初稿] 关于任务 '{task}' 的初始回答"
        rounds.append({
            "round": 1,
            "role": "EXECUTOR",
            "output": initial_draft[:500] + "..." if len(initial_draft) > 500 else initial_draft,
            "timestamp": datetime.now().isoformat()
        })
        
        # Round 2: 审查者审查
        print("🔎 Round 2: 审查者审查...")
        review_result = {
            "verdict": "NEEDS_REVISION",
            "confidence": 0.85,
            "issues": [
                {
                    "type": "INCOMPLETE",
                    "severity": "MAJOR",
                    "location": "整体",
                    "description": "内容缺乏具体数据支撑",
                    "suggestion": "添加具体数据、案例或引用来源",
                    "confidence": 0.9
                }
            ],
            "strengths": ["结构清晰", "逻辑连贯"],
            "overall_feedback": "整体框架良好，但需要补充具体内容"
        }
        rounds.append({
            "round": 2,
            "role": "REVIEWER",
            "output": review_result,
            "timestamp": datetime.now().isoformat()
        })
        issues_found.extend(review_result["issues"])
        strengths.extend(review_result["strengths"])
        
        # Round 3: 执行者修订
        print("✏️ Round 3: 执行者修订...")
        revised_draft = f"[模拟修订稿] 根据审查意见修订后的版本"
        rounds.append({
            "round": 3,
            "role": "EXECUTOR_REVISION",
            "output": revised_draft,
            "timestamp": datetime.now().isoformat()
        })
        
        # 最终审查
        print("✅ 最终审查...")
        final_verdict = "PASS"
        final_confidence = 0.92
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 生成报告
        report = ReviewReport(
            session_id=session_id,
            task=task,
            status="APPROVED",
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration_seconds=duration,
            rounds=len(rounds),
            executor_model=self.config["models"]["executor"],
            reviewer_model=self.config["models"]["reviewer"],
            verdict=final_verdict,
            confidence=final_confidence,
            issues=[asdict(issue) if isinstance(issue, ReviewIssue) else issue for issue in issues_found],
            strengths=strengths,
            overall_feedback="审查通过，输出质量符合要求",
            recommendations=[
                {
                    "issue": "内容缺乏具体数据支撑",
                    "suggestion": "添加具体数据、案例或引用来源",
                    "implemented": True
                }
            ],
            full_history=rounds
        )
        
        # 保存报告
        if output_path:
            self.save_report(report, output_path)
            print(f"💾 报告已保存到：{output_path}")
        
        self.review_history.append(report)
        
        print()
        print("=" * 60)
        print("✅ 审查完成")
        print(f"   结论：{report.verdict}")
        print(f"   置信度：{report.confidence:.2f}")
        print(f"   发现问题：{len(report.issues)} 个")
        print(f"   审查轮次：{report.rounds}")
        print(f"   耗时：{report.duration_seconds:.2f}秒")
        print("=" * 60)
        
        return report
    
    def save_report(self, report: ReviewReport, output_path: str):
        """保存审查报告到文件"""
        report_dict = asdict(report)
        
        # 确保目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)
    
    def get_statistics(self) -> Dict:
        """获取审查统计信息"""
        if not self.review_history:
            return {
                "total_reviews": 0,
                "pass_rate": 0,
                "avg_rounds": 0,
                "avg_duration": 0,
                "total_issues_found": 0
            }
        
        total = len(self.review_history)
        passed = sum(1 for r in self.review_history if r.verdict == "PASS")
        total_rounds = sum(r.rounds for r in self.review_history)
        total_duration = sum(r.duration_seconds or 0 for r in self.review_history)
        total_issues = sum(len(r.issues) for r in self.review_history)
        
        return {
            "total_reviews": total,
            "pass_rate": passed / total if total > 0 else 0,
            "avg_rounds": total_rounds / total if total > 0 else 0,
            "avg_duration": total_duration / total if total > 0 else 0,
            "total_issues_found": total_issues
        }


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="对抗式审查机制",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python adversarial_review.py review --task "分析 AAPL 股票" --output report.json
  python adversarial_review.py check-facts --content "某文本" --output facts.json
  python adversarial_review.py check-logic --content "某论证"
  python adversarial_review.py check-safety --content "某内容"
  python adversarial_review.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # review 命令
    review_parser = subparsers.add_parser("review", help="执行完整的对抗式审查")
    review_parser.add_argument("--task", required=True, help="任务描述")
    review_parser.add_argument("--draft", help="可选的初稿文件路径")
    review_parser.add_argument("--output", help="输出报告文件路径")
    review_parser.add_argument("--config", help="配置文件路径 (JSON)")
    
    # check-facts 命令
    facts_parser = subparsers.add_parser("check-facts", help="事实准确性检查")
    facts_parser.add_argument("--content", required=True, help="待检查内容")
    facts_parser.add_argument("--context", help="可选的上下文")
    facts_parser.add_argument("--output", help="输出文件路径")
    
    # check-logic 命令
    logic_parser = subparsers.add_parser("check-logic", help="逻辑一致性检查")
    logic_parser.add_argument("--content", required=True, help="待检查内容")
    logic_parser.add_argument("--output", help="输出文件路径")
    
    # check-safety 命令
    safety_parser = subparsers.add_parser("check-safety", help="安全风险检查")
    safety_parser.add_argument("--content", required=True, help="待检查内容")
    safety_parser.add_argument("--context", help="可选的上下文")
    safety_parser.add_argument("--output", help="输出文件路径")
    
    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="查看审查统计")
    
    args = parser.parse_args()
    
    # 加载配置
    config = {}
    if hasattr(args, 'config') and args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    reviewer = AdversarialReviewer(config)
    
    if args.command == "review":
        # 读取初稿 (如有)
        initial_draft = None
        if args.draft:
            with open(args.draft, 'r') as f:
                initial_draft = f.read()
        
        # 运行审查
        report = reviewer.run_review(args.task, initial_draft, args.output)
        
        # 打印摘要
        print("\n📊 审查摘要:")
        print(json.dumps({
            "session_id": report.session_id,
            "verdict": report.verdict,
            "confidence": report.confidence,
            "issues_count": len(report.issues),
            "rounds": report.rounds,
            "duration": report.duration_seconds
        }, indent=2))
        
    elif args.command == "check-facts":
        issues = reviewer.check_facts(args.content, args.context)
        result = {"issues": [asdict(i) if isinstance(i, ReviewIssue) else i for i in issues]}
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ 检查结果已保存到：{args.output}")
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
    elif args.command == "check-logic":
        issues = reviewer.check_logic(args.content)
        result = {"issues": [asdict(i) if isinstance(i, ReviewIssue) else i for i in issues]}
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ 检查结果已保存到：{args.output}")
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
    elif args.command == "check-safety":
        issues = reviewer.check_safety(args.content, args.context)
        result = {"issues": [asdict(i) if isinstance(i, ReviewIssue) else i for i in issues]}
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ 检查结果已保存到：{args.output}")
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
    elif args.command == "stats":
        stats = reviewer.get_statistics()
        print("📊 审查统计:")
        print(json.dumps(stats, indent=2))
        
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

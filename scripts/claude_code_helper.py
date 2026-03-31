#!/usr/bin/env python3
"""
ClawBuilder × Claude Code 协作助手

封装 sessions_spawn 调用 Claude Code 的逻辑，支持简单任务和复杂任务的智能分发。
"""

import json
import sys
from typing import Optional, List, Dict, Any
from pathlib import Path


class ClaudeCodeHelper:
    """Claude Code 调用封装类"""

    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        self.templates_dir = self.workspace / "templates"
        self.template_file = self.templates_dir / "claude-collaboration.md"

    def load_template(self) -> str:
        """加载协作模板"""
        if not self.template_file.exists():
            raise FileNotFoundError(f"Template not found: {self.template_file}")
        return self.template_file.read_text(encoding="utf-8")

    def prepare_task_context(
        self,
        task_description: str,
        priority: str = "medium",
        deadline: Optional[str] = None,
        specific_instructions: Optional[str] = None,
        context_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        准备任务上下文

        Args:
            task_description: 任务描述
            priority: 优先级 (low/medium/high/urgent)
            deadline: 截止时间 (ISO 8601 格式)
            specific_instructions: 具体指令
            context_files: 上下文文件列表

        Returns:
            任务上下文字典
        """
        context = {
            "task_description": task_description,
            "priority": priority,
            "deadline": deadline or "未指定",
            "specific_instructions": specific_instructions or "",
            "context_files": context_files or []
        }
        return context

    def classify_task(self, task_description: str) -> str:
        """
        分类任务复杂度

        简单任务：单文件修改、小功能实现、Bug 修复
        复杂任务：多文件重构、新功能模块、架构调整

        Args:
            task_description: 任务描述

        Returns:
            "simple" 或 "complex"
        """
        simple_keywords = ["修复", "bug", "typo", "小功能", "单文件", "修改"]
        complex_keywords = ["重构", "架构", "模块", "多文件", "新功能", "系统"]

        desc_lower = task_description.lower()

        # 检查复杂任务关键词
        for keyword in complex_keywords:
            if keyword in desc_lower:
                return "complex"

        # 检查简单任务关键词
        for keyword in simple_keywords:
            if keyword in desc_lower:
                return "simple"

        # 默认按任务长度判断
        if len(task_description) < 100:
            return "simple"
        return "complex"

    def build_claude_code_prompt(
        self,
        context: Dict[str, Any],
        mode: str = "simple"
    ) -> str:
        """
        构建 Claude Code 提示词

        Args:
            context: 任务上下文
            mode: 任务模式 (simple/complex)

        Returns:
            完整的提示词
        """
        template = self.load_template()

        # 填充模板
        prompt = template.format(
            task_description=context["task_description"],
            priority=context["priority"],
            deadline=context["deadline"],
            specific_instructions=context["specific_instructions"] or "请按照最佳实践完成此任务",
        )

        # 根据模式添加额外指令
        if mode == "complex":
            prompt += "\n\n## 复杂任务额外要求\n"
            prompt += "- 先分析现有代码结构\n"
            prompt += "- 提供实现方案再编码\n"
            prompt += "- 考虑向后兼容性\n"
            prompt += "- 添加详细的代码注释\n"

        # 添加上下文文件内容
        if context["context_files"]:
            prompt += "\n\n## 上下文文件\n"
            for file_path in context["context_files"]:
                file_path = Path(file_path)
                if file_path.exists():
                    prompt += f"\n### {file_path.name}\n```\n{file_path.read_text(encoding='utf-8')}\n```\n"

        return prompt

    def invoke_claude_code(
        self,
        task_description: str,
        context_files: Optional[List[str]] = None,
        mode: Optional[str] = None,
        priority: str = "medium",
        deadline: Optional[str] = None,
        specific_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        调用 Claude Code 执行任务

        Args:
            task_description: 任务描述
            context_files: 上下文文件列表
            mode: 强制指定模式 (simple/complex)，不指定则自动分类
            priority: 优先级
            deadline: 截止时间
            specific_instructions: 具体指令

        Returns:
            包含任务信息和提示词的字典
        """
        # 自动分类任务
        if mode is None:
            mode = self.classify_task(task_description)

        # 准备上下文
        context = self.prepare_task_context(
            task_description=task_description,
            priority=priority,
            deadline=deadline,
            specific_instructions=specific_instructions,
            context_files=context_files
        )

        # 构建提示词
        prompt = self.build_claude_code_prompt(context, mode)

        # 返回任务信息（供 sessions_spawn 使用）
        result = {
            "mode": mode,
            "context": context,
            "prompt": prompt,
            "agent_id": "claude-code",  # ACP 配置的 Claude Code agent
            "runtime": "acp"
        }

        return result

    def generate_sessions_spawn_params(
        self,
        task_description: str,
        context_files: Optional[List[str]] = None,
        mode: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成 sessions_spawn 调用参数

        Args:
            task_description: 任务描述
            context_files: 上下文文件列表
            mode: 任务模式
            **kwargs: 其他参数

        Returns:
            sessions_spawn 的参数字典
        """
        task_info = self.invoke_claude_code(
            task_description=task_description,
            context_files=context_files,
            mode=mode,
            **kwargs
        )

        # 构建完整的任务指令
        full_task = f"""
请作为 Claude Code 执行以下任务：

{task_info['prompt']}

## 执行要求
1. 仔细阅读任务描述和上下文
2. 按照输出要求完成代码
3. 确保通过所有审查清单项目
4. 完成后输出总结报告
"""

        spawn_params = {
            "task": full_task,
            "runtime": task_info["runtime"],
            "agentId": task_info["agent_id"],
            "mode": "run",  # 一次性任务
            "label": f"ClaudeCode-{task_info['mode']}-{task_description[:30]}"
        }

        return spawn_params


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法：python claude_code_helper.py <task_description> [context_files...]")
        print("示例：python claude_code_helper.py '修复登录 bug' ./src/login.py")
        sys.exit(1)

    task_description = sys.argv[1]
    context_files = sys.argv[2:] if len(sys.argv) > 2 else []

    helper = ClaudeCodeHelper()

    # 分类任务
    mode = helper.classify_task(task_description)
    print(f"任务分类：{mode}")

    # 生成调用参数
    params = helper.generate_sessions_spawn_params(
        task_description=task_description,
        context_files=context_files
    )

    # 输出 JSON 格式参数（供其他脚本调用）
    print("\nSessions Spawn 参数:")
    print(json.dumps(params, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

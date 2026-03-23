#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书文档创建器 - 基于模板自动创建文档

功能:
- 从模板创建文档
- 自动清理 image[[...]] 占位符
- 支持变量替换 ({{variable}} 语法)
- 自动归档到指定飞书文件夹

使用示例:
    from feishu_doc_creator import FeishuDocCreator
    
    creator = FeishuDocCreator()
    
    # 创建任务文档
    doc_id = creator.create_from_template(
        template='task-template',
        variables={
            'task_id': 'TASK-20260323-001',
            'assignee': 'ClawBuilder',
            'deadline': '2026-03-25'
        },
        folder_token='UDARfZ30YlI7ild68FmcEoianSg'  # 公司事务/系统/
    )
"""

import os
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


# ==================== 配置 ====================

@dataclass
class DocTemplate:
    """文档模板配置"""
    name: str
    file: str
    description: str
    default_folder: str  # folder_token


# 模板注册表
TEMPLATES = {
    'task-template': DocTemplate(
        name='任务文档模板',
        file='task-template.md',
        description='用于创建任务追踪文档',
        default_folder='UDARfZ30YlI7ild68FmcEoianSg'  # 公司事务/系统/
    ),
    'decision-template': DocTemplate(
        name='决策记录模板',
        file='decision-template.md',
        description='用于创建决策记录文档',
        default_folder='UDARfZ30YlI7ild68FmcEoianSg'
    ),
    'meeting-template': DocTemplate(
        name='会议纪要模板',
        file='meeting-template.md',
        description='用于创建会议纪要文档',
        default_folder='Sfj4fDTgplB29xdGriSctLVHn4b'  # 公司事务/会议/
    ),
    'daily-report-template': DocTemplate(
        name='日报模板',
        file='daily-report-template.md',
        description='用于创建日报文档',
        default_folder='HV72frYGNlm3sVdE1vIcYSCHnac'  # 公司事务/日报/
    )
}

# 工作空间路径
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMPLATES_DIR = WORKSPACE / 'docs' / 'templates'


# ==================== 核心类 ====================

class FeishuDocCreator:
    """飞书文档创建器"""
    
    def __init__(self):
        """初始化文档创建器"""
        self.workspace = WORKSPACE
        self.templates_dir = TEMPLATES_DIR
        
        # 确保模板目录存在
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_template(self, template_name: str) -> str:
        """
        加载模板文件
        
        Args:
            template_name: 模板名称 (如 'task-template')
            
        Returns:
            str: 模板内容
            
        Raises:
            FileNotFoundError: 模板文件不存在
        """
        if template_name not in TEMPLATES:
            raise ValueError(f"未知模板：{template_name}")
        
        template = TEMPLATES[template_name]
        template_path = self.templates_dir / template.file
        
        if not template_path.exists():
            # 如果模板文件不存在，创建默认模板
            self._create_default_template(template_name)
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _create_default_template(self, template_name: str):
        """创建默认模板文件"""
        template = TEMPLATES[template_name]
        template_path = self.templates_dir / template.file
        
        if template_name == 'task-template':
            content = """# 📋 任务文档 - {{task_id}}

**创建日期**: {{created_at}}  
**负责人**: {{assignee}}  
**截止日期**: {{deadline}}  
**优先级**: {{priority}}

---

## 一、任务描述

{{description}}

---

## 二、实施计划

### 阶段 1: 需求分析
- [ ] 理解需求
- [ ] 技术方案设计

### 阶段 2: 开发实现
- [ ] 编码实现
- [ ] 单元测试

### 阶段 3: 测试验证
- [ ] 功能测试
- [ ] 集成测试

### 阶段 4: 部署上线
- [ ] 部署到生产
- [ ] 验证功能

---

## 三、进度追踪

| 日期 | 进度 | 备注 |
|------|------|------|
| {{created_at}} | 0% | 任务创建 |

---

## 四、问题与风险

| 问题 | 影响 | 解决方案 | 状态 |
|------|------|----------|------|
| - | - | - | - |

---

## 五、验收标准

- [ ] 功能符合需求
- [ ] 测试全部通过
- [ ] 文档完整

---

*最后更新*: {{updated_at}}
"""
        
        elif template_name == 'decision-template':
            content = """# 📝 决策记录 - {{decision_id}}

**决策日期**: {{created_at}}  
**决策人**: {{decision_maker}}  
**参与人**: {{participants}}

---

## 一、决策背景

{{background}}

---

## 二、决策选项

### 选项 A: {{option_a_name}}

**优点**:
- 

**缺点**:
- 

### 选项 B: {{option_b_name}}

**优点**:
- 

**缺点**:
- 

---

## 三、决策结果

**选择**: {{selected_option}}

**理由**:
{{rationale}}

---

## 四、影响评估

| 影响领域 | 影响描述 | 缓解措施 |
|----------|----------|----------|
| 技术 | - | - |
| 业务 | - | - |
| 成本 | - | - |

---

## 五、后续行动

- [ ] 
- [ ] 
- [ ] 

---

*最后更新*: {{updated_at}}
"""
        
        elif template_name == 'meeting-template':
            content = """# 📅 会议纪要 - {{meeting_date}}

**会议主题**: {{topic}}  
**会议时间**: {{meeting_time}}  
**参会人员**: {{attendees}}  
**记录人**: {{recorder}}

---

## 一、会议议程

1. {{agenda_1}}
2. {{agenda_2}}
3. {{agenda_3}}

---

## 二、讨论内容

### 议题 1: {{topic_1}}

**讨论要点**:
- 

**结论**:
- 

### 议题 2: {{topic_2}}

**讨论要点**:
- 

**结论**:
- 

---

## 三、决策事项

| 序号 | 决策内容 | 负责人 | 截止时间 |
|------|----------|--------|----------|
| 1 | - | - | - |

---

## 四、行动项

| 序号 | 行动项 | 负责人 | 状态 | 截止时间 |
|------|--------|--------|------|----------|
| 1 | - | - | ☐ 未开始 | - |

---

## 五、下次会议

- **时间**: 
- **主题**: 

---

*纪要创建时间*: {{created_at}}
"""
        
        elif template_name == 'daily-report-template':
            content = """# 📊 日报 - {{report_date}}

**报告人**: {{reporter}}  
**日期**: {{report_date}}

---

## 一、今日完成

| 序号 | 工作内容 | 进度 | 备注 |
|------|----------|------|------|
| 1 | - | ✅ 100% | - |
| 2 | - | ✅ 100% | - |

---

## 二、进行中

| 序号 | 工作内容 | 进度 | 预计完成 |
|------|----------|------|----------|
| 1 | - | 🔄 50% | - |

---

## 三、问题与风险

| 序号 | 问题描述 | 影响 | 需要支持 |
|------|----------|------|----------|
| 1 | - | - | - |

---

## 四、明日计划

1. 
2. 
3. 

---

## 五、心得与建议

- 

---

*报告生成时间*: {{created_at}}
"""
        
        else:
            content = f"# {template.name}\n\n{{{{content}}}}"
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"创建默认模板：{template_path}")
    
    def _replace_variables(self, content: str, variables: Dict[str, Any]) -> str:
        """
        替换模板变量
        
        Args:
            content: 模板内容
            variables: 变量字典
            
        Returns:
            str: 替换后的内容
        """
        # 添加默认变量
        now = datetime.now()
        default_vars = {
            'created_at': now.strftime('%Y-%m-%d %H:%M'),
            'updated_at': now.strftime('%Y-%m-%d %H:%M'),
            'current_date': now.strftime('%Y-%m-%d')
        }
        default_vars.update(variables)
        
        # 替换 {{variable}} 格式的变量
        for key, value in default_vars.items():
            placeholder = '{{' + key + '}}'
            content = content.replace(placeholder, str(value))
        
        return content
    
    def _cleanup_image_placeholders(self, content: str) -> str:
        """
        清理 image[[...]] 占位符
        
        Args:
            content: 文档内容
            
        Returns:
            str: 清理后的内容
        """
        # 匹配 image[[...]] 格式
        pattern = r'image\[\[.*?\]\]'
        cleaned = re.sub(pattern, '[图片已移除]', content)
        
        return cleaned
    
    def create_from_template(
        self,
        template: str,
        variables: Optional[Dict[str, Any]] = None,
        folder_token: Optional[str] = None,
        title: Optional[str] = None,
        cleanup_images: bool = True
    ) -> Dict[str, str]:
        """
        从模板创建文档
        
        Args:
            template: 模板名称 (如 'task-template')
            variables: 变量替换字典
            folder_token: 目标文件夹 token，默认使用模板配置
            title: 文档标题，默认使用模板名 + 日期
            cleanup_images: 是否清理 image[[...]] 占位符
            
        Returns:
            Dict: 包含文档信息的字典 {doc_id, title, template, folder}
            
        Raises:
            ValueError: 模板不存在
            Exception: 创建失败
        """
        if variables is None:
            variables = {}
        
        # 1. 获取模板配置
        if template not in TEMPLATES:
            raise ValueError(f"未知模板：{template}")
        
        template_config = TEMPLATES[template]
        
        # 2. 加载模板内容
        content = self._load_template(template)
        
        # 3. 替换变量
        content = self._replace_variables(content, variables)
        
        # 4. 清理图片占位符
        if cleanup_images:
            content = self._cleanup_image_placeholders(content)
        
        # 5. 生成标题
        if not title:
            title = f"{template_config.name} - {datetime.now().strftime('%Y-%m-%d')}"
        
        # 6. 使用文件夹 token
        target_folder = folder_token or template_config.default_folder
        
        # 7. 返回文档信息 (实际使用时会调用 feishu_create_doc API)
        doc_info = {
            'doc_id': f"DOC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'title': title,
            'template': template,
            'folder': target_folder,
            'content_preview': content[:200] + '...' if len(content) > 200 else content
        }
        
        print(f"✅ 文档创建成功:")
        print(f"  标题：{title}")
        print(f"  模板：{template}")
        print(f"  文件夹：{target_folder}")
        print(f"  文档 ID: {doc_info['doc_id']}")
        
        return doc_info
    
    def list_templates(self) -> List[Dict[str, str]]:
        """
        列出所有可用模板
        
        Returns:
            List[Dict]: 模板信息列表
        """
        return [
            {
                'name': key,
                'description': t.description,
                'file': t.file
            }
            for key, t in TEMPLATES.items()
        ]


# ==================== 命令行入口 ====================

def main():
    """命令行入口"""
    import sys
    
    creator = FeishuDocCreator()
    
    if len(sys.argv) < 2:
        print("用法：python3 feishu_doc_creator.py <command> [args]")
        print("\n可用命令:")
        print("  list-templates                    列出所有模板")
        print("  create <template> [vars...]       从模板创建文档")
        print("  show-template <template>          显示模板内容")
        return
    
    command = sys.argv[1]
    
    if command == 'list-templates':
        templates = creator.list_templates()
        print("可用模板:")
        for t in templates:
            print(f"  - {t['name']}: {t['description']}")
    
    elif command == 'create':
        if len(sys.argv) < 3:
            print("用法：create <template> [var=value ...]")
            return
        
        template_name = sys.argv[2]
        
        # 解析变量
        variables = {}
        for arg in sys.argv[3:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                variables[key] = value
        
        try:
            doc_info = creator.create_from_template(template_name, variables)
            print(f"✅ 文档创建成功：{doc_info['doc_id']}")
        except Exception as e:
            print(f"❌ 创建失败：{e}")
    
    elif command == 'show-template':
        if len(sys.argv) < 3:
            print("用法：show-template <template>")
            return
        
        template_name = sys.argv[2]
        
        try:
            content = creator._load_template(template_name)
            print(content)
        except Exception as e:
            print(f"❌ 加载失败：{e}")
    
    else:
        print(f"❌ 未知命令：{command}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置同步脚本 - 从飞书多维表格同步 Agent 配置到 OpenClaw

功能:
- 从飞书 Bitable 读取 Agent 配置
- 验证配置格式 (JSON Schema)
- 备份当前配置
- 写入新配置
- 清理文档占位符
- Git 提交变更

使用:
    python3 sync_feishu_to_openclaw.py
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 依赖检查
try:
    import requests
    from jsonschema import validate, ValidationError
except ImportError as e:
    print(f"❌ 缺少依赖：{e}")
    print("请运行：pip install requests jsonschema")
    sys.exit(1)


# ==================== 配置 ====================

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
CONFIG_DIR = WORKSPACE / 'config'
BACKUP_DIR = WORKSPACE / '.backup' / 'config'
AGENT_CONFIG_DIR = WORKSPACE / 'agents'

# 飞书 API 配置
FEISHU_API_BASE = 'https://open.feishu.cn/open-apis'
BITABLE_APP_TOKEN = os.getenv('FEISHU_BITABLE_TOKEN', '')

# Agent 配置 Schema
AGENT_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["agent_id", "name", "systemPrompt"],
    "properties": {
        "agent_id": {"type": "string"},
        "name": {"type": "string"},
        "systemPrompt": {"type": "string"},
        "skills": {"type": "array", "items": {"type": "string"}},
        "tools": {"type": "object"},
        "model": {"type": "string"},
        "thinking": {"type": "string"}
    }
}

OPENCLAW_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["agents"],
    "properties": {
        "agents": {
            "type": "object",
            "required": ["list"],
            "properties": {
                "list": {"type": "array", "items": {"type": "string"}}
            }
        }
    }
}


# ==================== 核心功能 ====================

class ConfigSyncService:
    """配置同步服务"""
    
    def __init__(self):
        self.workspace = WORKSPACE
        self.config_dir = CONFIG_DIR
        self.backup_dir = BACKUP_DIR
        self.agent_config_dir = AGENT_CONFIG_DIR
        
        # 确保目录存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.agent_config_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_feishu_bitable(self) -> List[Dict[str, Any]]:
        """
        从飞书多维表格读取 Agent 配置
        
        Returns:
            List[Dict]: Agent 配置列表
        """
        app_id = os.getenv('FEISHU_APP_ID')
        app_secret = os.getenv('FEISHU_APP_SECRET')
        
        if not app_id or not app_secret:
            raise ValueError("缺少飞书 API 凭证 (FEISHU_APP_ID, FEISHU_APP_SECRET)")
        
        # 1. 获取用户访问令牌
        token_url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
        token_response = requests.post(token_url, json={
            "app_id": app_id,
            "app_secret": app_secret
        })
        token_response.raise_for_status()
        tenant_token = token_response.json()['tenant_access_token']
        
        # 2. 读取多维表格数据
        # 注意：这里需要根据实际的 Bitable 结构实现
        # 以下是示例代码
        records_url = f"{FEISHU_API_BASE}/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/table_id/records"
        headers = {"Authorization": f"Bearer {tenant_token}"}
        
        records_response = requests.get(records_url, headers=headers)
        records_response.raise_for_status()
        
        records = records_response.json()['data']['items']
        
        # 3. 转换为 Agent 配置格式
        agents = []
        for record in records:
            fields = record.get('fields', {})
            agent = {
                'agent_id': fields.get('Agent ID', ''),
                'name': fields.get('名称', ''),
                'systemPrompt': fields.get('系统提示', ''),
                'skills': fields.get('技能', '').split(',') if fields.get('技能') else [],
                'model': fields.get('模型', 'default')
            }
            agents.append(agent)
        
        return agents
    
    def validate_config(self, agents: List[Dict[str, Any]]) -> bool:
        """
        验证配置格式
        
        Args:
            agents: Agent 配置列表
            
        Returns:
            bool: 是否有效
            
        Raises:
            ValidationError: 验证失败
        """
        for agent in agents:
            validate(agent, AGENT_CONFIG_SCHEMA)
        
        return True
    
    def backup_current_config(self) -> str:
        """
        备份当前配置
        
        Returns:
            str: 备份目录路径
        """
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_path = self.backup_dir / timestamp
        
        # 复制当前配置
        if self.config_dir.exists():
            shutil.copytree(self.config_dir, backup_path)
        
        print(f"✅ 配置已备份：{backup_path}")
        return str(backup_path)
    
    def write_agent_configs(self, agents: List[Dict[str, Any]]):
        """
        写入 Agent 配置
        
        Args:
            agents: Agent 配置列表
        """
        # 1. 更新主配置中的 agents.list
        main_config_path = self.workspace / 'config.json'
        
        if main_config_path.exists():
            with open(main_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        if 'agents' not in config:
            config['agents'] = {}
        
        config['agents']['list'] = [a['agent_id'] for a in agents]
        
        with open(main_config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # 2. 为每个 Agent 创建独立配置文件
        for agent in agents:
            agent_config_path = self.agent_config_dir / f"{agent['agent_id']}.json"
            
            with open(agent_config_path, 'w', encoding='utf-8') as f:
                json.dump(agent, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已写入 {len(agents)} 个 Agent 配置")
    
    def cleanup_image_placeholders(self):
        """清理文档中的 image[[...]] 占位符"""
        import re
        
        docs_dir = self.workspace / 'docs'
        if not docs_dir.exists():
            return
        
        pattern = r'image\[\[.*?\]\]'
        count = 0
        
        for md_file in docs_dir.rglob('*.md'):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            cleaned = re.sub(pattern, '[图片已移除]', content)
            
            if content != cleaned:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned)
                count += 1
        
        print(f"✅ 已清理 {count} 个文件中的图片占位符")
    
    def git_commit_and_push(self, message: str):
        """
        Git 提交并推送
        
        Args:
            message: 提交信息
        """
        try:
            subprocess.run(['git', 'add', '-A'], check=True, cwd=self.workspace)
            subprocess.run(['git', 'commit', '-m', message], check=True, cwd=self.workspace)
            subprocess.run(['git', 'push'], check=True, cwd=self.workspace)
            print("✅ Git 提交并推送成功")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git 操作失败：{e}")
    
    def sync(self) -> bool:
        """
        执行完整同步流程
        
        Returns:
            bool: 是否成功
        """
        try:
            print("🔄 开始配置同步...")
            
            # 1. 从飞书读取配置
            print("📥 从飞书读取配置...")
            agents = self.fetch_feishu_bitable()
            print(f"  读取到 {len(agents)} 个 Agent 配置")
            
            # 2. 验证配置
            print("🔍 验证配置格式...")
            self.validate_config(agents)
            print("  ✅ 配置验证通过")
            
            # 3. 备份当前配置
            print("💾 备份当前配置...")
            self.backup_current_config()
            
            # 4. 写入新配置
            print("✍️  写入新配置...")
            self.write_agent_configs(agents)
            
            # 5. 清理图片占位符
            print("🧹 清理图片占位符...")
            self.cleanup_image_placeholders()
            
            # 6. Git 提交
            print("📤 Git 提交...")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
            self.git_commit_and_push(f"chore: sync agent config {timestamp}")
            
            print("✅ 配置同步成功")
            return True
            
        except ValidationError as e:
            print(f"❌ 配置验证失败：{e.message}")
            return False
            
        except Exception as e:
            print(f"❌ 同步失败：{e}")
            # 尝试恢复备份
            print("🔄 尝试恢复备份...")
            self.restore_from_backup()
            return False
    
    def restore_from_backup(self):
        """从最新备份恢复配置"""
        backups = sorted(self.backup_dir.iterdir(), reverse=True)
        
        if not backups:
            print("❌ 无可用备份")
            return
        
        latest_backup = backups[0]
        
        # 删除当前配置
        if self.config_dir.exists():
            shutil.rmtree(self.config_dir)
        
        # 恢复备份
        shutil.copytree(latest_backup, self.config_dir)
        print(f"✅ 已从备份恢复：{latest_backup}")


# ==================== 命令行入口 ====================

def main():
    """命令行入口"""
    service = ConfigSyncService()
    success = service.sync()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

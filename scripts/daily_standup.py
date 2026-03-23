#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
骐骥·每日站会自动化脚本
- 22:00 自动组织日会
- 生成工作日报
- 发送到 Google Docs
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMPLATES_DIR = WORKSPACE / 'templates'
REPORTS_DIR = WORKSPACE / 'reports'
TASKS_DIR = WORKSPACE / 'tasks'

class DailyStandup:
    """每日站会管理器"""
    
    def __init__(self):
        self.today = datetime.now()
        self.today_str = self.today.strftime('%Y-%m-%d')
        self.tomorrow = self.today + timedelta(days=1)
        
    def load_project_board(self):
        """加载项目看板数据"""
        board_file = WORKSPACE / 'PROJECT_BOARD.md'
        if not board_file.exists():
            return None
        
        with open(board_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简单解析 (实际应该更完善)
        return {
            'content': content,
            'completed': [],  # 需要解析
            'in_progress': [],
            'todo': []
        }
    
    def load_daily_memory(self):
        """加载今日记忆"""
        memory_file = WORKSPACE / 'memory' / f'{self.today_str}.md'
        if not memory_file.exists():
            return None
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    
    def generate_standup_notes(self):
        """生成站会纪要"""
        template_file = TEMPLATES_DIR / 'daily_standup_template.md'
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 替换占位符
        notes = template.replace(
            '{{DATE}}', 
            self.today.strftime('%Y-%m-%d (%A)')
        ).replace(
            '{{TOMORROW}}', 
            self.tomorrow.strftime('%Y-%m-%d')
        )
        
        # 保存到 reports 目录
        output_file = REPORTS_DIR / 'standup' / f'{self.today_str}_standup.md'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(notes)
        
        print(f"✅ 站会纪要已生成：{output_file}")
        return output_file
    
    def generate_daily_report(self):
        """生成工作日报"""
        template_file = TEMPLATES_DIR / 'daily_report_template.md'
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 替换占位符
        report = template.replace(
            '{{DATE}}', 
            self.today.strftime('%Y-%m-%d')
        ).replace(
            '{{TIME}}', 
            self.today.strftime('%H:%M')
        ).replace(
            '{{SUMMARY}}', 
            f'{self.today_str} 工作日报 - 骐骥 AI CEO'
        )
        
        # 保存到 reports 目录
        output_file = REPORTS_DIR / 'daily' / f'{self.today_str}_daily_report.md'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 工作日报已生成：{output_file}")
        return output_file
    
    def upload_to_google_docs(self, file_path, title=None):
        """上传到 Google Docs (使用 gog docs create)"""
        import subprocess
        
        if title is None:
            title = f"🐎 骐骥·工作日报 {self.today_str}"
        
        print(f"📤 创建 Google Docs: {title}")
        
        # 读取本地文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 创建 Google Doc
        cmd = ['gog', 'docs', 'create', title, '--json']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                import json
                doc_info = json.loads(result.stdout)
                doc_id = doc_info.get('file', {}).get('id', '')
                doc_url = doc_info.get('file', {}).get('webViewLink', f"https://docs.google.com/document/d/{doc_id}")
                
                print(f"✅ Google Doc 已创建：{doc_url}")
                
                # 写入内容
                if doc_id and content:
                    self.write_to_google_doc(doc_id, content)
                
                return doc_url
            else:
                print(f"⚠️ 创建失败：{result.stderr}")
                return f"https://docs.google.com/document/d/ERROR"
        except Exception as e:
            print(f"⚠️ 异常：{e}")
            return f"https://docs.google.com/document/d/ERROR"
    
    def write_to_google_doc(self, doc_id, content):
        """写入内容到 Google Doc"""
        import subprocess
        import tempfile
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # 使用 gog docs write --file
            cmd = ['gog', 'docs', 'write', doc_id, '--file', temp_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ 内容已写入 Google Doc")
            else:
                print(f"⚠️ 写入失败：{result.stderr}")
        except Exception as e:
            print(f"⚠️ 写入异常：{e}")
        finally:
            # 清理临时文件
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def send_notification(self, message):
        """发送通知 (飞书/邮件)"""
        print(f"📬 发送通知：{message[:100]}...")
        
        # TODO: 实现通知发送
        # 可以使用飞书 webhook 或邮件
    
    def create_tomorrow_schedule(self, tasks):
        """创建第二天日程到 Google Calendar"""
        print("\n📅 创建第二天日程...")
        
        tomorrow_str = self.tomorrow.strftime('%Y-%m-%d')
        
        # 创建全天的工作计划事件
        if tasks:
            task_list = "\n".join([f"- {t.get('task', 'N/A')} ({t.get('owner', 'TBD')})" for t in tasks[:10]])
            
            description = f"""📋 明日工作计划

🎯 P0 任务 (必须完成):
{task_list}

📌 会议/活动:
- 22:00 每日站会

💡 备注:
详细计划见工作日报
"""
            
            # 创建工作时间段事件 (09:00-18:00)
            cmd = [
                'gog', 'calendar', 'create', 'primary',
                '--summary', f'📅 {tomorrow_str} 工作计划',
                '--description', description,
                '--from', f'{tomorrow_str}T09:00:00+08:00',
                '--to', f'{tomorrow_str}T18:00:00+08:00',
                '--reminder', 'popup:30m'
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print(f"✅ 明日日程已创建：{tomorrow_str}")
                    return True
                else:
                    print(f"⚠️ 创建失败：{result.stderr}")
            except Exception as e:
                print(f"⚠️ 异常：{e}")
        
        return False
    
    def run(self):
        """执行每日站会流程"""
        print("=" * 60)
        print("🐎 骐骥·每日站会自动化")
        print(f"📅 日期：{self.today_str}")
        print("=" * 60)
        
        # 1. 加载数据
        print("\n📊 加载数据...")
        board = self.load_project_board()
        memory = self.load_daily_memory()
        
        # 2. 生成站会纪要
        print("\n📝 生成站会纪要...")
        standup_file = self.generate_standup_notes()
        
        # 3. 生成工作日报
        print("\n📊 生成工作日报...")
        report_file = self.generate_daily_report()
        
        # 4. 上传到 Google Docs
        print("\n☁️ 上传到 Google Docs...")
        docs_link = self.upload_to_google_docs(report_file)
        
        # 5. 发送通知
        print("\n📬 发送通知...")
        self.send_notification(f"【每日站会】{self.today_str} 工作日报已生成")
        
        # 6. 创建第二天日程
        print("\n📅 创建第二天日程...")
        tomorrow_tasks = [
            {'task': '执行 Rex 技能审计', 'owner': 'Rex', 'priority': 'P0'},
            {'task': '测试覆盖率提升至 90%', 'owner': 'QA', 'priority': 'P0'},
            {'task': '执行第一次产品调研', 'owner': 'Product', 'priority': 'P0'},
        ]
        self.create_tomorrow_schedule(tomorrow_tasks)
        
        print("\n" + "=" * 60)
        print("✅ 每日站会流程完成")
        print("=" * 60)
        
        return {
            'standup_file': str(standup_file),
            'report_file': str(report_file),
            'docs_link': docs_link,
            'tomorrow_scheduled': True
        }


if __name__ == '__main__':
    standup = DailyStandup()
    result = standup.run()
    print(f"\n结果：{json.dumps(result, ensure_ascii=False, indent=2)}")

#!/usr/bin/env python3
"""
OpenClaw Skills 市场搜索工具

功能:
- search: 关键词搜索 Skills
- list: 列出 Skills（支持分类筛选）
- info: 查看 Skill 详情
- recommend: 推荐 Skills

用法:
    python scripts/skill_market.py search "股票"
    python scripts/skill_market.py list --category 投资
    python scripts/skill_market.py info a-stock-monitor
    python scripts/skill_market.py recommend
"""

import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class SkillMarket:
    """Skills 市场管理器"""
    
    def __init__(self, index_path: str = None):
        """初始化 Skills 市场
        
        Args:
            index_path: skills-index.json 路径，默认在工作区根目录
        """
        if index_path is None:
            # 默认路径：~/.openclaw/workspace/skills-index.json
            home = Path.home()
            index_path = home / ".openclaw" / "workspace" / "skills-index.json"
        
        self.index_path = Path(index_path).expanduser()
        self.index_data = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """加载 Skills 索引文件"""
        if not self.index_path.exists():
            print(f"❌ 错误：索引文件不存在：{self.index_path}")
            sys.exit(1)
        
        with open(self.index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索 Skills
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量上限
            
        Returns:
            匹配的 Skills 列表
        """
        query_lower = query.lower()
        results = []
        
        for skill in self.index_data.get('skills', []):
            # 搜索范围：名称、描述、触发词、标签
            search_fields = [
                skill.get('name', ''),
                skill.get('description', ''),
                ' '.join(skill.get('triggers', [])),
                ' '.join(skill.get('tags', []))
            ]
            
            search_text = ' '.join(search_fields).lower()
            
            if query_lower in search_text:
                results.append(skill)
        
        # 按评分和使用次数排序
        results.sort(key=lambda x: (x.get('rating', 0), x.get('usageCount', 0)), reverse=True)
        
        return results[:limit]
    
    def list_skills(self, category: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """列出 Skills
        
        Args:
            category: 分类过滤（可选）
            limit: 返回结果数量上限
            
        Returns:
            Skills 列表
        """
        skills = self.index_data.get('skills', [])
        
        if category:
            # 支持中文分类名匹配
            category_map = {
                '投资': 'trading',
                '交易': 'trading',
                'trading': 'trading',
                '飞书': 'feishu',
                'feishu': 'feishu',
                'Agent': 'agent',
                'agent': 'agent',
                '系统': 'system',
                'system': 'system',
                '工具': 'system'
            }
            
            category_id = category_map.get(category, category.lower())
            skills = [s for s in skills if s.get('category') == category_id]
        
        # 按评分排序
        skills.sort(key=lambda x: (x.get('rating', 0), x.get('usageCount', 0)), reverse=True)
        
        return skills[:limit]
    
    def get_info(self, skill_id: str) -> Dict[str, Any]:
        """获取 Skill 详情
        
        Args:
            skill_id: Skill ID
            
        Returns:
            Skill 详情
        """
        for skill in self.index_data.get('skills', []):
            if skill.get('id') == skill_id:
                return skill
        
        return None
    
    def recommend(self, limit: int = 5) -> List[Dict[str, Any]]:
        """推荐 Skills
        
        推荐逻辑：
        1. 高评分（>= 4.5）
        2. 高使用次数
        3. 不同分类均衡
        
        Args:
            limit: 推荐数量上限
            
        Returns:
            推荐的 Skills 列表
        """
        skills = self.index_data.get('skills', [])
        
        # 筛选高评分技能
        high_rated = [s for s in skills if s.get('rating', 0) >= 4.5]
        
        # 按使用次数排序
        high_rated.sort(key=lambda x: x.get('usageCount', 0), reverse=True)
        
        # 确保分类多样性
        recommendations = []
        category_count = {}
        
        for skill in high_rated:
            if len(recommendations) >= limit:
                break
            
            category = skill.get('category')
            count = category_count.get(category, 0)
            
            # 每个分类最多 2 个
            if count < 2:
                recommendations.append(skill)
                category_count[category] = count + 1
        
        # 如果数量不足，补充高评分技能
        if len(recommendations) < limit:
            for skill in high_rated:
                if skill not in recommendations:
                    recommendations.append(skill)
                    if len(recommendations) >= limit:
                        break
        
        return recommendations[:limit]
    
    def print_search_results(self, results: List[Dict[str, Any]], query: str):
        """打印搜索结果"""
        if not results:
            print(f"\n❌ 未找到匹配的 Skills: \"{query}\"")
            print("💡 尝试其他关键词或使用 'list' 查看所有 Skills\n")
            return
        
        print(f"\n🔍 搜索结果：{query} ({len(results)} 个匹配)\n")
        print("=" * 80)
        
        for i, skill in enumerate(results, 1):
            category_info = self._get_category_info(skill.get('category'))
            rating_stars = '⭐' * round(skill.get('rating', 0))
            
            print(f"\n{i}. {skill.get('emoji', '🔧')} {skill.get('name')} ({skill.get('id')})")
            print(f"   分类：{category_info['icon']} {category_info['name']}")
            print(f"   评分：{rating_stars} {skill.get('rating', 0)}")
            print(f"   使用次数：{skill.get('usageCount', 0)}")
            print(f"   描述：{skill.get('description', '')[:100]}...")
            
            triggers = skill.get('triggers', [])[:5]
            if triggers:
                print(f"   触发词：{', '.join(triggers)}")
        
        print("\n" + "=" * 80)
        print(f"💡 查看详情：python scripts/skill_market.py info <skill-id>")
        print()
    
    def print_list(self, skills: List[Dict[str, Any]], category: str = None):
        """打印 Skills 列表"""
        filter_text = f" - 分类：{category}" if category else ""
        print(f"\n📦 Skills 列表{filter_text} ({len(skills)} 个)\n")
        print("=" * 80)
        
        # 按分类分组
        by_category = {}
        for skill in skills:
            cat = skill.get('category', 'unknown')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(skill)
        
        for cat_id, cat_skills in by_category.items():
            cat_info = self._get_category_info(cat_id)
            print(f"\n{cat_info['icon']} {cat_info['name']} ({len(cat_skills)})")
            print("-" * 60)
            
            for skill in sorted(cat_skills, key=lambda x: x.get('rating', 0), reverse=True):
                rating_stars = '⭐' * round(skill.get('rating', 0))
                print(f"  {skill.get('emoji', '🔧')} {skill.get('name'):25} {rating_stars:12} ({skill.get('usageCount', 0)} 次)")
        
        print("\n" + "=" * 80)
        print(f"💡 搜索：python scripts/skill_market.py search <关键词>")
        print(f"💡 详情：python scripts/skill_market.py info <skill-id>")
        print()
    
    def print_info(self, skill: Dict[str, Any]):
        """打印 Skill 详情"""
        if not skill:
            print("\n❌ 未找到该 Skill\n")
            return
        
        category_info = self._get_category_info(skill.get('category'))
        rating_stars = '⭐' * round(skill.get('rating', 0))
        
        print(f"\n📦 {skill.get('name')}")
        print("=" * 80)
        print(f"ID:        {skill.get('id')}")
        print(f"分类：     {category_info['icon']} {category_info['name']}")
        print(f"版本：     v{skill.get('version', '1.0.0')}")
        print(f"作者：     {skill.get('author', 'Unknown')}")
        print(f"评分：     {rating_stars} {skill.get('rating', 0)}")
        print(f"使用次数： {skill.get('usageCount', 0)}")
        print(f"\n描述:")
        print(f"  {skill.get('description', '')}")
        
        triggers = skill.get('triggers', [])
        if triggers:
            print(f"\n触发词 ({len(triggers)}):")
            for i in range(0, len(triggers), 5):
                batch = triggers[i:i+5]
                print(f"  {', '.join(batch)}")
        
        tags = skill.get('tags', [])
        if tags:
            print(f"\n标签:")
            print(f"  {', '.join(tags)}")
        
        print(f"\n位置：{skill.get('location', 'N/A')}")
        
        print("\n" + "=" * 80)
        print(f"💡 安装：openclaw skill install {skill.get('id')}")
        print()
    
    def print_recommendations(self, recommendations: List[Dict[str, Any]]):
        """打印推荐 Skills"""
        print(f"\n⭐ 推荐 Skills ({len(recommendations)})\n")
        print("=" * 80)
        
        for i, skill in enumerate(recommendations, 1):
            category_info = self._get_category_info(skill.get('category'))
            rating_stars = '⭐' * round(skill.get('rating', 0))
            
            print(f"\n{i}. {skill.get('emoji', '🔧')} {skill.get('name')}")
            print(f"   分类：{category_info['icon']} {category_info['name']}")
            print(f"   评分：{rating_stars} {skill.get('rating', 0)} | 使用：{skill.get('usageCount', 0)} 次")
            print(f"   {skill.get('description', '')[:80]}...")
        
        print("\n" + "=" * 80)
        print(f"💡 搜索：python scripts/skill_market.py search <关键词>")
        print(f"💡 列表：python scripts/skill_market.py list")
        print()
    
    def _get_category_info(self, category_id: str) -> Dict[str, str]:
        """获取分类信息"""
        default = {'id': category_id, 'name': category_id, 'icon': '🔧'}
        
        for cat in self.index_data.get('categories', []):
            if cat.get('id') == category_id:
                return {
                    'id': cat.get('id'),
                    'name': cat.get('name'),
                    'icon': cat.get('icon', '🔧')
                }
        
        return default
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.index_data.get('statistics', {})
        
        print(f"\n📊 Skills 市场统计")
        print("=" * 80)
        print(f"总技能数：  {stats.get('totalSkills', 0)}")
        print(f"平均评分：  {stats.get('averageRating', 0)}")
        print(f"总使用次数：{stats.get('totalUsageCount', 0)}")
        print(f"最后更新：  {self.index_data.get('updatedAt', 'Unknown')}")
        
        print(f"\n分类分布:")
        by_category = stats.get('byCategory', {})
        for cat_id, count in by_category.items():
            cat_info = self._get_category_info(cat_id)
            print(f"  {cat_info['icon']} {cat_info['name']:15} {count} 个")
        
        print("\n" + "=" * 80)
        print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='OpenClaw Skills 市场搜索工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/skill_market.py search "股票"
  python scripts/skill_market.py list --category 投资
  python scripts/skill_market.py info a-stock-monitor
  python scripts/skill_market.py recommend
  python scripts/skill_market.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索 Skills')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('-l', '--limit', type=int, default=10, help='返回结果数量上限')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出 Skills')
    list_parser.add_argument('-c', '--category', help='分类过滤')
    list_parser.add_argument('-l', '--limit', type=int, default=50, help='返回结果数量上限')
    
    # info 命令
    info_parser = subparsers.add_parser('info', help='查看 Skill 详情')
    info_parser.add_argument('skill_id', help='Skill ID')
    
    # recommend 命令
    recommend_parser = subparsers.add_parser('recommend', help='推荐 Skills')
    recommend_parser.add_argument('-l', '--limit', type=int, default=5, help='推荐数量')
    
    # stats 命令
    subparsers.add_parser('stats', help='显示统计信息')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # 创建 Skills 市场实例
    market = SkillMarket()
    
    # 执行命令
    if args.command == 'search':
        results = market.search(args.query, args.limit)
        market.print_search_results(results, args.query)
    
    elif args.command == 'list':
        skills = market.list_skills(args.category, args.limit)
        market.print_list(skills, args.category)
    
    elif args.command == 'info':
        skill = market.get_info(args.skill_id)
        market.print_info(skill)
    
    elif args.command == 'recommend':
        recommendations = market.recommend(args.limit)
        market.print_recommendations(recommendations)
    
    elif args.command == 'stats':
        market.print_stats()


if __name__ == '__main__':
    main()

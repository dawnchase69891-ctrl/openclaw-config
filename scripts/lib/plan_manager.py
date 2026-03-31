#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调仓计划管理器
管理调仓计划的增删改查、价格刷新、自动失效
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class RebalancePlanManager:
    """调仓计划管理器"""

    def __init__(self, data_dir: str = None):
        """
        初始化计划管理器

        Args:
            data_dir: 数据目录路径（默认为 scripts/data）
        """
        if data_dir is None:
            # 默认路径：scripts/../data
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(os.path.dirname(script_dir), 'data')

        self.plans_file = os.path.join(data_dir, 'rebalance_plans.json')
        self.history_file = os.path.join(data_dir, 'rebalance_history.json')

        # 确保目录和文件存在
        self._init_data_dir()

    def _init_data_dir(self):
        """初始化数据目录和文件"""
        # 创建目录
        os.makedirs(os.path.dirname(self.plans_file), exist_ok=True)

        # 初始化计划文件
        if not os.path.exists(self.plans_file):
            self._save_plans({
                'plans': [],
                'metadata': {
                    'last_refresh': datetime.now().strftime('%Y-%m-%d'),
                    'version': '1.0'
                }
            })

        # 初始化历史文件
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _load_plans(self) -> Dict:
        """加载计划数据"""
        with open(self.plans_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_plans(self, data: Dict):
        """保存计划数据"""
        with open(self.plans_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_plan(self, plan: Dict) -> str:
        """
        添加新计划

        Args:
            plan: 计划字典，包含 stock, code, action, quantity, target_price, priority, reason

        Returns:
            计划 ID
        """
        data = self._load_plans()

        # 生成 ID
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 补充必要字段
        plan.update({
            'id': plan_id,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'active',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'expiry_threshold': 0.10,  # 默认 10% 偏离阈值
            'base_price': plan.get('target_price', 0),  # 基准价格（默认为目标价）
            'current_price': 0.0
        })

        data['plans'].append(plan)

        # 更新元数据
        data['metadata']['last_refresh'] = datetime.now().strftime('%Y-%m-%d')

        self._save_plans(data)

        return plan_id

    def get_all_plans(self) -> List[Dict]:
        """获取所有计划"""
        data = self._load_plans()
        return data.get('plans', [])

    def get_active_plans(self) -> List[Dict]:
        """获取活跃计划"""
        all_plans = self.get_all_plans()
        return [p for p in all_plans if p.get('status') == 'active']

    def get_plan_by_id(self, plan_id: str) -> Optional[Dict]:
        """根据 ID 获取计划"""
        all_plans = self.get_all_plans()
        for plan in all_plans:
            if plan.get('id') == plan_id:
                return plan
        return None

    def update_plan_price(self, plan_id: str, current_price: float):
        """
        更新计划的价格

        Args:
            plan_id: 计划 ID
            current_price: 当前价格
        """
        data = self._load_plans()

        for plan in data['plans']:
            if plan.get('id') == plan_id:
                plan['current_price'] = current_price
                plan['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # 检查是否需要失效
                self._check_expiry(plan)
                break

        self._save_plans(data)

    def _check_expiry(self, plan: Dict):
        """
        检查计划是否需要失效

        Args:
            plan: 计划字典（会被修改）
        """
        if plan.get('status') != 'active':
            return

        base_price = plan.get('base_price', 0)
        current_price = plan.get('current_price', 0)
        threshold = plan.get('expiry_threshold', 0.10)

        if base_price == 0 or current_price == 0:
            return

        # 计算偏离度
        deviation = abs(current_price - base_price) / base_price

        if deviation > threshold:
            plan['status'] = 'expired'
            plan['expiry_reason'] = f'价格偏离 {deviation*100:.1f}% 超过阈值 {threshold*100:.0f}%'
            plan['expiry_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            print(f"⚠️  {plan['stock']} 计划已失效: {plan['expiry_reason']}")

    def refresh_all_prices(self, price_service):
        """
        刷新所有计划的价格

        Args:
            price_service: 价格服务实例
        """
        active_plans = self.get_active_plans()

        for plan in active_plans:
            code = plan.get('code')
            if code:
                current_price = price_service.get_price(code)

                if current_price is not None:
                    self.update_plan_price(plan['id'], current_price)
                    print(f"✅ {plan['stock']} ({code}) 价格已更新: ¥{current_price:.2f}")
                else:
                    print(f"❌ {plan['stock']} ({code}) 价格获取失败")

    def mark_executed(self, plan_id: str):
        """
        标记计划为已执行

        Args:
            plan_id: 计划 ID
        """
        data = self._load_plans()

        for plan in data['plans']:
            if plan.get('id') == plan_id:
                plan['status'] = 'executed'
                plan['executed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # 记录到历史
                self._add_to_history(plan)
                break

        self._save_plans(data)

    def _add_to_history(self, plan: Dict):
        """将计划添加到历史记录"""
        history = self._load_history()

        history.append({
            'id': plan['id'],
            'stock': plan['stock'],
            'code': plan['code'],
            'action': plan['action'],
            'quantity': plan['quantity'],
            'target_price': plan['target_price'],
            'executed_price': plan.get('current_price', 0),
            'executed_date': plan['executed_date'],
            'reason': plan.get('reason', '')
        })

        self._save_history(history)

    def _load_history(self) -> List:
        """加载历史记录"""
        with open(self.history_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_history(self, history: List):
        """保存历史记录"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def delete_plan(self, plan_id: str):
        """
        删除计划

        Args:
            plan_id: 计划 ID
        """
        data = self._load_plans()

        data['plans'] = [p for p in data['plans'] if p.get('id') != plan_id]

        self._save_plans(data)

    def clear_expired_plans(self):
        """清除所有过期计划"""
        data = self._load_plans()

        expired_count = len([p for p in data['plans'] if p.get('status') == 'expired'])
        data['plans'] = [p for p in data['plans'] if p.get('status') != 'expired']

        self._save_plans(data)

        print(f"✅ 已清除 {expired_count} 个过期计划")

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        all_plans = self.get_all_plans()

        active_count = len([p for p in all_plans if p.get('status') == 'active'])
        expired_count = len([p for p in all_plans if p.get('status') == 'expired'])
        executed_count = len([p for p in all_plans if p.get('status') == 'executed'])

        return {
            'total': len(all_plans),
            'active': active_count,
            'expired': expired_count,
            'executed': executed_count
        }


if __name__ == '__main__':
    # 测试计划管理器
    manager = RebalancePlanManager()

    print("📊 统计信息:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n📋 所有计划:")
    for plan in manager.get_all_plans():
        status = plan.get('status', 'unknown')
        print(f"  [{status}] {plan['stock']} {plan['action']} {plan['quantity']}股 @ ¥{plan['target_price']}")
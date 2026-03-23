#!/usr/bin/env python3
"""
角色路由模块 - 解析群消息中的 @角色名 并返回对应的 agentId

支持的角色：Rex, ClawHunter, ClawBreaker, ClawBuilder, ClawGuard, ClawOps
"""
from typing import Optional, Dict

# 角色名到 agentId 的映射配置
ROLE_AGENT_MAP = {
    "Rex": "rexi",
    "ClawHunter": "clawhunter",
    "ClawBreaker": "clawbreaker",
    "ClawBuilder": "clawbuilder",
    "ClawGuard": "clawguard",
    "ClawOps": "clawops",
}

# 群 ID 配置
TARGET_GROUP_ID = "oc_88d2f2fdba3985ce4af408c6084faff1"


def parse_role_mention(message_text: str) -> Optional[str]:
    """
    解析消息中的 @角色名，返回匹配的角色名
    
    Args:
        message_text: 消息文本
        
    Returns:
        匹配到的角色名，如果没有匹配则返回 None
    """
    for role_name in ROLE_AGENT_MAP.keys():
        # 支持多种 @ 格式：@Rex, @Rex , @Rex!
        if f"@{role_name}" in message_text:
            return role_name
    return None


def get_agent_id(role_name: str) -> Optional[str]:
    """
    根据角色名获取对应的 agentId
    
    Args:
        role_name: 角色名（如 "Rex", "ClawHunter" 等）
        
    Returns:
        对应的 agentId，如果角色不存在则返回 None
    """
    return ROLE_AGENT_MAP.get(role_name)


def route_message(message_text: str, chat_id: Optional[str] = None) -> Dict:
    """
    路由消息 - 解析 @角色名 并返回路由信息
    
    Args:
        message_text: 消息文本
        chat_id: 群 ID（可选，用于验证是否在目标群）
        
    Returns:
        路由结果字典：
        - success: bool，是否成功路由
        - role: str | None，匹配到的角色名
        - agent_id: str | None，对应的 agentId
        - error: str | None，错误信息（如果有）
    """
    # 可选：验证群 ID
    if chat_id and chat_id != TARGET_GROUP_ID:
        return {
            "success": False,
            "role": None,
            "agent_id": None,
            "error": f"非目标群聊：{chat_id}",
        }
    
    # 解析角色名
    role_name = parse_role_mention(message_text)
    
    if not role_name:
        return {
            "success": False,
            "role": None,
            "agent_id": None,
            "error": "未找到有效的 @角色名",
        }
    
    # 获取 agentId
    agent_id = get_agent_id(role_name)
    
    if not agent_id:
        return {
            "success": False,
            "role": role_name,
            "agent_id": None,
            "error": f"角色 {role_name} 未配置 agentId",
        }
    
    return {
        "success": True,
        "role": role_name,
        "agent_id": agent_id,
        "error": None,
    }


# 测试代码
if __name__ == "__main__":
    # 测试用例
    test_cases = [
        "@Rex 你好",
        "请 @ClawHunter 处理一下",
        "@ClawBuilder 帮我写个代码",
        "@ClawGuard 检查一下安全",
        "@ClawOps 部署服务",
        "@ClawBreaker 突破限制",
        "没有 @ 的消息",
        "@Unknown 未知角色",
    ]
    
    print("角色路由测试：\n")
    for test in test_cases:
        result = route_message(test)
        status = "✅" if result["success"] else "❌"
        print(f"{status} 消息：{test}")
        print(f"   角色：{result['role']}, AgentID: {result['agent_id']}")
        if result["error"]:
            print(f"   错误：{result['error']}")
        print()

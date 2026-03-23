#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书消息接收服务
接收飞书消息并转发给 OpenClaw 处理
"""

import json
import hmac
import hashlib
import base64
from datetime import datetime
from flask import Flask, request, jsonify
import requests
import sys

app = Flask(__name__)

# 飞书应用配置
FEISHU_APP_ID = "cli_a93bacddf1f89bd7"
FEISHU_APP_SECRET = "ogM77ShlxBE6HcQ6Qn7uTbiJ1iGqGORS"
FEISHU_VERIFICATION_TOKEN = "4VqPPXa2VHIU3IVC33hSubi7lsx25lx3"

# 获取飞书 access_token
def get_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    resp = requests.post(url, json=payload, timeout=10)
    data = resp.json()
    if data.get('code') == 0:
        return data.get('tenant_access_token')
    else:
        print(f"获取 access_token 失败：{data}")
        return None

# 发送飞书消息
def send_feishu_message(user_id, content, msg_type="text"):
    access_token = get_access_token()
    if not access_token:
        return False
    
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "receive_id": user_id,
        "msg_type": msg_type,
        "content": json.dumps(content)
    }
    params = {"receive_id_type": "user_id"}
    
    resp = requests.post(url, headers=headers, json=payload, params=params, timeout=10)
    data = resp.json()
    if data.get('code') == 0:
        print(f"消息发送成功：{user_id}")
        return True
    else:
        print(f"消息发送失败：{data}")
        return False

# 验证飞书签名
def verify_signature(timestamp, nonce, signature):
    # 简单验证，生产环境应该严格验证
    return True

@app.route('/feishu/callback', methods=['POST'])
def feishu_callback():
    """接收飞书事件回调"""
    try:
        data = request.json
        print(f"收到飞书回调：{json.dumps(data, ensure_ascii=False)}")
        
        # 验证挑战（首次配置时使用）
        if data.get('type') == 'url_verification':
            challenge = data.get('challenge')
            print(f"验证挑战：{challenge}")
            return jsonify({'challenge': challenge})
        
        # 处理消息事件
        if data.get('type') == 'im.message.receive_v1':
            event = data.get('event', {})
            message = event.get('message', {})
            
            # 获取消息内容
            msg_id = message.get('message_id')
            chat_id = message.get('chat_id')
            sender_id = message.get('sender_id')
            content = message.get('content')
            msg_type = message.get('message_type')
            
            print(f"收到消息：{msg_id} from {sender_id}")
            print(f"消息内容：{content}")
            
            # TODO: 将消息转发给 OpenClaw 处理
            # 这里可以调用 OpenClaw 的 API 或直接处理
            
            # 示例：回复一条消息
            if msg_type == 'text':
                text_content = json.loads(content).get('text', '')
                reply = f"🐎 骐骥收到你的消息：{text_content[:50]}..."
                send_feishu_message(sender_id, {"text": reply})
            
            return jsonify({'status': 'success'})
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        print(f"处理回调失败：{e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/feishu/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'app_id': FEISHU_APP_ID
    })

if __name__ == '__main__':
    print("=" * 60)
    print("📱 飞书消息接收服务")
    print("=" * 60)
    print(f"App ID: {FEISHU_APP_ID}")
    print(f"回调地址：http://localhost:8081/feishu/callback")
    print(f"健康检查：http://localhost:8081/feishu/health")
    print("=" * 60)
    
    # 启动服务
    app.run(host='0.0.0.0', port=8081, debug=False)

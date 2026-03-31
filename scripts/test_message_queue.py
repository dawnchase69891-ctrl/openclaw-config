#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试消息队列功能
"""

import time
from lib.message_queue import MessageQueue, get_message_queue, send_message_later


def test_sender(msg):
    """测试发送函数"""
    print(f"发送消息: {msg}")
    return True  # 模拟发送成功


def main():
    print("开始测试消息队列...")
    
    # 获取消息队列实例
    queue = get_message_queue()
    queue.set_sender(test_sender)
    
    # 添加几条测试消息
    print("\n添加测试消息到队列...")
    send_message_later({"title": "测试消息1", "content": "这是第一条测试消息"}, 2)
    send_message_later({"title": "测试消息2", "content": "这是第二条测试消息"}, 5)
    send_message_later({"title": "测试消息3", "content": "这是第三条测试消息"}, 1)
    
    print("消息已添加到队列，等待发送...")
    print("队列信息:", queue.queue.qsize(), "条消息待处理")
    
    # 让程序运行一段时间以处理消息
    time.sleep(10)
    
    print("\n停止消息队列...")
    queue.stop()
    print("测试完成")


if __name__ == "__main__":
    main()
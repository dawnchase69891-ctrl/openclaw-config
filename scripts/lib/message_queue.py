"""
飞书消息队列管理模块
实现消息入队、定时发送、错误重试等功能
"""
import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from queue import Queue, Empty


class MessageQueue:
    """
    飞书消息队列类
    支持消息入队、定时发送、错误重试等功能
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 5.0):
        """
        初始化消息队列
        
        Args:
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）
        """
        self.queue = Queue()
        self.running = False
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
        self.sender_func = None
        
    def set_sender(self, sender_func: Callable):
        """
        设置消息发送函数
        
        Args:
            sender_func: 消息发送函数，接受消息参数并返回发送结果
        """
        self.sender_func = sender_func
    
    def enqueue_message(self, message_data: Dict, delay: float = 0.0):
        """
        将消息加入队列
        
        Args:
            message_data: 消息数据
            delay: 延迟发送时间（秒）
        """
        send_time = datetime.now() + timedelta(seconds=delay)
        item = {
            'message': message_data,
            'send_time': send_time,
            'retry_count': 0,
            'original_send_time': send_time
        }
        self.queue.put(item)
        self.logger.info(f"消息已加入队列，预计发送时间: {send_time}")
        
    def start(self):
        """启动消息队列处理器"""
        if self.running:
            return
        self.running = True
        self.processor_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processor_thread.start()
        self.logger.info("消息队列处理器已启动")
        
    def stop(self):
        """停止消息队列处理器"""
        self.running = False
        if hasattr(self, 'processor_thread'):
            self.processor_thread.join(timeout=5)
        self.logger.info("消息队列处理器已停止")
        
    def _process_queue(self):
        """处理消息队列的后台线程函数"""
        while self.running:
            try:
                # 检查是否有到期的消息
                self._handle_scheduled_messages()
                
                # 等待一段时间再检查
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"处理消息队列时发生错误: {e}")
                
    def _handle_scheduled_messages(self):
        """处理定时消息"""
        # 临时队列存储未到期的消息
        temp_queue = []
        
        # 检查当前队列中的所有消息
        while True:
            try:
                item = self.queue.get_nowait()
                current_time = datetime.now()
                
                # 检查消息是否到期
                if current_time >= item['send_time']:
                    # 消息到期，尝试发送
                    success = self._send_message(item)
                    if not success:
                        # 发送失败，根据重试次数决定是否重新入队
                        if item['retry_count'] < self.max_retries:
                            # 增加重试次数和下次发送时间
                            item['retry_count'] += 1
                            item['send_time'] = current_time + timedelta(seconds=self.retry_delay)
                            self.logger.warning(
                                f"消息发送失败，第 {item['retry_count']} 次重试，"
                                f"将在 {self.retry_delay} 秒后重试"
                            )
                            temp_queue.append(item)
                        else:
                            self.logger.error(f"消息重试次数已达上限，丢弃消息: {item['message']}")
                else:
                    # 消息未到期，放回临时队列
                    temp_queue.append(item)
                    
            except Empty:
                # 队列为空，跳出循环
                break
                
        # 将未到期的消息重新放回队列
        for item in temp_queue:
            self.queue.put(item)
            
    def _send_message(self, item: Dict) -> bool:
        """
        发送单条消息
        
        Args:
            item: 消息项目
            
        Returns:
            bool: 发送是否成功
        """
        if not self.sender_func:
            self.logger.error("未设置消息发送函数")
            return False
            
        try:
            result = self.sender_func(item['message'])
            if result:
                self.logger.info(f"消息发送成功: {item['message'].get('title', 'Unknown')}")
                return True
            else:
                self.logger.error(f"消息发送失败: {item['message'].get('title', 'Unknown')}")
                return False
        except Exception as e:
            self.logger.error(f"发送消息时发生异常: {e}")
            return False


# 全局消息队列实例
_global_message_queue = None


def get_message_queue(max_retries: int = 3, retry_delay: float = 5.0) -> MessageQueue:
    """
    获取全局消息队列实例
    
    Args:
        max_retries: 最大重试次数
        retry_delay: 重试延迟时间
        
    Returns:
        MessageQueue: 消息队列实例
    """
    global _global_message_queue
    if _global_message_queue is None:
        _global_message_queue = MessageQueue(max_retries, retry_delay)
        _global_message_queue.start()
    return _global_message_queue


def send_message_later(message_data: Dict, delay: float = 0.0):
    """
    延迟发送消息
    
    Args:
        message_data: 消息数据
        delay: 延迟时间（秒）
    """
    queue = get_message_queue()
    queue.enqueue_message(message_data, delay)


if __name__ == "__main__":
    # 测试代码
    import threading
    
    def test_sender(msg):
        print(f"发送消息: {msg}")
        return True  # 模拟发送成功
        
    queue = get_message_queue()
    queue.set_sender(test_sender)
    
    # 添加几条测试消息
    send_message_later({"title": "测试消息1", "content": "这是第一条测试消息"}, 2)
    send_message_later({"title": "测试消息2", "content": "这是第二条测试消息"}, 5)
    
    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        queue.stop()
        print("程序已退出")
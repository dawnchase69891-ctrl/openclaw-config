"""
增强版飞书消息队列系统 - 解决频率限制问题
实现消息入队、定时发送、错误重试机制，并针对飞书API进行优化
"""

import asyncio
import threading
import time
from collections import deque
from typing import Dict, List, Optional, Callable
import logging
from datetime import datetime
import json
import requests


class EnhancedMessageQueue:
    """增强版飞书消息队列"""
    
    def __init__(self, max_size: int = 100, send_interval: float = 2.0, max_retries: int = 3):
        """
        初始化消息队列
        
        Args:
            max_size: 队列最大容量
            send_interval: 发送间隔（秒）
            max_retries: 最大重试次数
        """
        self.queue = deque(maxlen=max_size)
        self.max_retries = max_retries
        self.send_interval = send_interval  # 控制发送频率
        self.lock = threading.Lock()
        self.is_running = False
        self.worker_thread = None
        self.logger = self._setup_logger()
        
        # 频率限制相关参数
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_window = 60  # 60秒窗口
        self.rate_limit_max = 100  # 每分钟最多100次请求
        
    def _setup_logger(self):
        """设置日志"""
        logger = logging.getLogger('EnhancedMessageQueue')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    def push(self, message: Dict) -> bool:
        """
        添加消息到队列
        
        Args:
            message: 消息内容，包含发送函数和参数
            
        Returns:
            bool: 是否成功添加
        """
        with self.lock:
            if len(self.queue) >= self.queue.maxlen:
                self.logger.warning("队列已满，丢弃消息")
                return False
            
            # 添加时间戳
            message['timestamp'] = time.time()
            message['attempts'] = 0
            message['priority'] = message.get('priority', 1)  # 1为普通优先级
            self.queue.append(message)
            
            # 按优先级重新排序（高优先级在前）
            temp_list = list(self.queue)
            temp_list.sort(key=lambda x: x.get('priority', 1), reverse=True)
            self.queue = deque(temp_list, maxlen=self.queue.maxlen)
            
            self.logger.info(f"消息入队，当前队列长度: {len(self.queue)}, 优先级: {message.get('priority', 1)}")
            return True

    def _check_rate_limit(self) -> bool:
        """检查是否达到速率限制"""
        current_time = time.time()
        
        # 如果超过时间窗口，重置计数
        if current_time - self.last_request_time > self.rate_limit_window:
            self.request_count = 0
            self.last_request_time = current_time
        
        # 检查是否超过限制
        if self.request_count >= self.rate_limit_max:
            wait_time = self.rate_limit_window - (current_time - self.last_request_time)
            if wait_time > 0:
                self.logger.info(f"接近速率限制，等待 {wait_time:.1f} 秒")
                time.sleep(wait_time)
                self.request_count = 0
                self.last_request_time = time.time()
                return True
            else:
                return False
        
        return True

    def _update_rate_counter(self):
        """更新请求计数器"""
        current_time = time.time()
        if current_time - self.last_request_time > self.rate_limit_window:
            self.request_count = 0
            self.last_request_time = current_time
        
        self.request_count += 1

    def _send_with_retry(self, message: Dict) -> bool:
        """
        带重试机制的消息发送
        
        Args:
            message: 消息内容
            
        Returns:
            bool: 是否发送成功
        """
        for attempt in range(self.max_retries + 1):
            try:
                # 检查速率限制
                if not self._check_rate_limit():
                    self.logger.warning("超过速率限制，跳过发送")
                    return False
                
                # 执行发送函数
                sender_func = message['sender_func']
                args = message.get('args', [])
                kwargs = message.get('kwargs', {})
                
                result = sender_func(*args, **kwargs)
                
                # 更新速率计数器
                self._update_rate_counter()
                
                if result:
                    self.logger.info(f"消息发送成功: {message.get('content', 'Unknown')[:50]}...")
                    return True
                else:
                    self.logger.warning(f"消息发送失败 (尝试 {attempt + 1}/{self.max_retries + 1})")
                    
            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"发送异常 (尝试 {attempt + 1}/{self.max_retries + 1}): {error_msg}")
                
                # 检查是否是频率限制错误
                if ('frequency limited' in error_msg.lower() or 
                    '11232' in error_msg or 
                    'rate limit' in error_msg.lower() or
                    'too many requests' in error_msg.lower()):
                    # 遇到频率限制，等待更长时间
                    wait_time = min(10 * (attempt + 1), 60)  # 最长等待60秒
                    self.logger.info(f"检测到频率限制，等待 {wait_time} 秒后重试")
                    time.sleep(wait_time)
                    continue
                    
            # 指数退避
            if attempt < self.max_retries:
                wait_time = 2 ** attempt  # 指数退避
                self.logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        self.logger.error(f"消息发送失败，已达最大重试次数: {message.get('content', 'Unknown')[:50]}...")
        return False

    def _worker(self):
        """后台工作线程"""
        self.logger.info("增强版消息队列工作线程启动")
        
        while self.is_running:
            try:
                with self.lock:
                    if self.queue:
                        message = self.queue.popleft()
                    else:
                        # 队列为空，短暂休眠
                        time.sleep(0.1)
                        continue
                
                # 发送消息
                success = self._send_with_retry(message)
                
                if not success:
                    # 发送失败，可以选择重新加入队列（但要限制重试次数）
                    with self.lock:
                        message['attempts'] += 1
                        if message['attempts'] <= self.max_retries:
                            # 重新加入队列尾部，但降低优先级
                            message['priority'] = max(1, message['priority'] - 1)
                            self.queue.append(message)
                            self.logger.info(f"消息重新入队，剩余重试次数: {self.max_retries - message['attempts']}")
                        else:
                            self.logger.error(f"消息发送彻底失败，丢弃消息: {message.get('content', 'Unknown')[:50]}...")
                
                # 控制发送频率
                time.sleep(self.send_interval)
                
            except Exception as e:
                self.logger.error(f"工作线程异常: {e}")
                time.sleep(1)  # 异常时稍作等待

    def start(self):
        """启动消息队列"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()
            self.logger.info("增强版消息队列已启动")

    def stop(self):
        """停止消息队列"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)  # 最多等待5秒
        self.logger.info("消息队列已停止")

    def get_queue_status(self) -> Dict:
        """获取队列状态"""
        with self.lock:
            return {
                'queue_length': len(self.queue),
                'max_size': self.queue.maxlen,
                'is_running': self.is_running,
                'request_count': self.request_count,
                'last_request_time': self.last_request_time,
                'rate_limit_remaining': max(0, self.rate_limit_max - self.request_count)
            }

    def flush(self):
        """清空队列"""
        with self.lock:
            count = len(self.queue)
            self.queue.clear()
            self.logger.info(f"队列已清空，共清空 {count} 条消息")


class FeishuAPIClient:
    """飞书API客户端，封装常用API调用"""
    
    def __init__(self, webhook_url: str, secret: Optional[str] = None):
        self.webhook_url = webhook_url
        self.secret = secret
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json; charset=utf-8'
        })
    
    def _generate_signature(self, timestamp: str) -> str:
        """生成飞书 webhook 签名"""
        if not self.secret:
            return ""
        
        import hashlib
        import hmac
        import base64
        
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        
        return base64.b64encode(hmac_code).decode("utf-8")
    
    def send_webhook_message(self, message: Dict) -> bool:
        """
        发送webhook消息
        
        Args:
            message: 消息内容，格式参考飞书API
            
        Returns:
            bool: 是否发送成功
        """
        try:
            # 添加签名
            timestamp = str(int(time.time()))
            params = {}
            
            if self.secret:
                signature = self._generate_signature(timestamp)
                params = {
                    "timestamp": timestamp,
                    "sign": signature
                }
            
            response = self.session.post(
                self.webhook_url,
                json=message,
                params=params,
                timeout=10
            )
            
            result = response.json()
            
            if result.get("StatusCode") == 0 or result.get("code") == 0:
                return True
            else:
                error_msg = result.get("msg", "Unknown error")
                raise Exception(f"API Error: {error_msg}")
                
        except Exception as e:
            print(f"❌ 发送消息异常：{e}")
            raise


# 全局消息队列实例
_enhanced_feishu_message_queue = None


def get_enhanced_message_queue() -> EnhancedMessageQueue:
    """获取全局增强版消息队列实例"""
    global _enhanced_feishu_message_queue
    if _enhanced_feishu_message_queue is None:
        _enhanced_feishu_message_queue = EnhancedMessageQueue()
        _enhanced_feishu_message_queue.start()
    return _enhanced_feishu_message_queue


def send_message_later(sender_func: Callable, priority: int = 1, *args, **kwargs) -> bool:
    """
    延迟发送消息（加入队列）
    
    Args:
        sender_func: 发送函数
        priority: 优先级（1-5，5为最高优先级）
        *args: 函数参数
        **kwargs: 函数关键字参数
        
    Returns:
        bool: 是否成功加入队列
    """
    queue = get_enhanced_message_queue()
    
    message = {
        'sender_func': sender_func,
        'args': args,
        'kwargs': kwargs,
        'content': kwargs.get('content', str(args)) if kwargs else str(args),
        'priority': priority
    }
    
    return queue.push(message)


def send_batch_messages(sender_func: Callable, messages: List[Dict], priority: int = 1) -> bool:
    """
    批量发送消息（合并为一条或多条发送）
    
    Args:
        sender_func: 发送函数
        messages: 消息列表
        priority: 优先级
        
    Returns:
        bool: 是否全部加入队列
    """
    if not messages:
        return True
    
    # 合并消息内容
    combined_content = "\n\n".join([
        msg.get('content', str(msg)) for msg in messages
    ])
    
    # 如果内容太长，可以分批发送
    max_content_length = 2000  # 飞书消息长度限制
    if len(combined_content) <= max_content_length:
        # 单条发送
        kwargs = messages[0].copy()
        kwargs['content'] = combined_content
        return send_message_later(sender_func, priority=priority, **kwargs)
    else:
        # 分批发送
        success = True
        current_batch = []
        current_length = 0
        
        for msg in messages:
            msg_content = msg.get('content', str(msg))
            if current_length + len(msg_content) > max_content_length:
                # 发送当前批次
                batch_content = "\n\n".join([
                    m.get('content', str(m)) for m in current_batch
                ])
                kwargs = current_batch[0].copy()
                kwargs['content'] = batch_content
                if not send_message_later(sender_func, priority=priority, **kwargs):
                    success = False
                
                # 开始新批次
                current_batch = [msg]
                current_length = len(msg_content)
            else:
                current_batch.append(msg)
                current_length += len(msg_content)
        
        # 发送最后一个批次
        if current_batch:
            batch_content = "\n\n".join([
                m.get('content', str(m)) for m in current_batch
            ])
            kwargs = current_batch[0].copy()
            kwargs['content'] = batch_content
            if not send_message_later(sender_func, priority=priority, **kwargs):
                success = False
        
        return success


def send_feishu_webhook_message(webhook_url: str, secret: Optional[str], message: Dict, priority: int = 1) -> bool:
    """
    通过消息队列发送飞书webhook消息
    
    Args:
        webhook_url: 飞书webhook URL
        secret: 签名密钥
        message: 消息内容
        priority: 优先级
        
    Returns:
        bool: 是否成功加入队列
    """
    client = FeishuAPIClient(webhook_url, secret)
    
    def send_func(msg_dict):
        return client.send_webhook_message(msg_dict)
    
    return send_message_later(send_func, priority, message)


# 示例使用方法
if __name__ == "__main__":
    # 示例：如何使用增强版消息队列发送飞书消息
    def mock_feishu_send(content: str, **kwargs):
        """模拟飞书发送函数"""
        print(f"发送消息: {content}")
        # 模拟偶尔的频率限制错误
        import random
        if random.random() < 0.1:  # 10%概率模拟频率限制
            raise Exception("frequency limited psm[lark.oapi.app_platform_runtime]appID[1500]")
        return True
    
    # 启动队列
    queue = get_enhanced_message_queue()
    
    # 添加几条消息到队列，包含不同优先级
    for i in range(3):
        send_message_later(mock_feishu_send, priority=3, content=f"普通消息 {i+1}", title=f"标题 {i+1}")
    
    # 添加高优先级消息
    send_message_later(mock_feishu_send, priority=5, content="高优先级消息", title="重要通知")
    
    # 批量发送
    batch_msgs = [
        {'content': '批量消息 1'},
        {'content': '批量消息 2'},
        {'content': '批量消息 3'},
    ]
    send_batch_messages(mock_feishu_send, batch_msgs, priority=2)
    
    # 显示队列状态
    print("队列状态:", queue.get_queue_status())
    
    # 等待一段时间让消息发送
    time.sleep(15)
    
    # 停止队列
    queue.stop()
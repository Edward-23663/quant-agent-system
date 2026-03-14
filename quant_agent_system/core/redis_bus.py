# core/redis_bus.py
import json
import logging
import redis
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RedisBus:
    """
    统一消息总线
    封装 Redis 操作，隔离底层的 List, Pub/Sub, Stream 逻辑
    """
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        # 开启 decode_responses=True 确保返回的都是 str 而非 bytes
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    # ================= 1. 队列机制 (List) =================
    def push_to_queue(self, queue_name: str, payload: Dict[str, Any]):
        """将任务推入队列尾部 (用于触发数据采集等异步任务)"""
        try:
            self.client.rpush(queue_name, json.dumps(payload))
        except Exception as e:
            logger.error(f"Redis 队列推送失败 [{queue_name}]: {e}")

    def pop_from_queue(self, queue_name: str, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """阻塞式从队列头部获取任务"""
        result = self.client.blpop(queue_name, timeout=timeout)
        if result:
            return json.loads(result[1])
        return None

    # ================= 2. 广播机制 (Pub/Sub) =================
    def publish_status(self, task_id: str, message: str):
        """发布任务状态广播 (Web UI 的 SSE 接口和主编排器监听此频道)"""
        channel = f"task_status:{task_id}"
        try:
            self.client.publish(channel, message)
            # 同时在控制台打印，方便本地调试
            print(f"📡 {message}") 
        except Exception as e:
            logger.error(f"Redis 广播发布失败 [{channel}]: {e}")

    # ================= 3. 数据流机制 (Stream) =================
    def add_to_stream(self, stream_name: str, payload: Dict[str, Any]) -> str:
        """
        推入数据流 (用于 Data Writer Worker 的安全串行写库)
        注意：Redis Stream 的 value 必须是 string/bytes。
        """
        # 将 payload 中的非字符串值转为 JSON 字符串
        stream_payload = {
            k: (v if isinstance(v, str) else json.dumps(v)) 
            for k, v in payload.items()
        }
        try:
            msg_id = self.client.xadd(stream_name, stream_payload)
            return msg_id
        except Exception as e:
            logger.error(f"Redis Stream 推送失败 [{stream_name}]: {e}")
            raise

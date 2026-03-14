# quant_agent_system/data/sync_scheduler.py
import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from sync_config import SYNC_TABLES_CONFIG, DEFAULT_SYNC_INTERVAL_HOURS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyncScheduler:
    def __init__(self, sync_service):
        self.scheduler = BackgroundScheduler()
        self.sync_service = sync_service
        self.config = SYNC_TABLES_CONFIG
        self._running = False
    
    def start(self, interval_hours: int = None):
        """启动定时调度"""
        interval = interval_hours or DEFAULT_SYNC_INTERVAL_HOURS
        
        if self._running:
            logger.warning("调度器已在运行中")
            return
        
        self.scheduler.add_job(
            self.sync_all,
            trigger=IntervalTrigger(hours=interval),
            id='db_sync_all',
            name='全量数据库同步',
            replace_existing=True
        )
        
        self.scheduler.start()
        self._running = True
        logger.info(f"✅ 同步调度器已启动 (间隔: {interval} 小时)")
    
    def stop(self):
        """停止调度"""
        if self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("同步调度器已停止")
    
    def sync_all(self):
        """执行全量同步"""
        logger.info("开始执行定时同步任务...")
        try:
            result = self.sync_service.trigger_sync()
            logger.info(f"定时同步完成: {result}")
            return result
        except Exception as e:
            logger.error(f"定时同步失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def is_running(self) -> bool:
        """检查调度器是否运行"""
        return self._running
    
    def get_next_run(self) -> Optional[str]:
        """获取下次运行时间"""
        job = self.scheduler.get_job('db_sync_all')
        if job and job.next_run_time:
            return job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
        return None


if __name__ == "__main__":
    from sync_service import SyncService
    svc = SyncService()
    sched = SyncScheduler(svc)
    sched.start(interval_hours=1)
    import time
    time.sleep(5)
    sched.stop()

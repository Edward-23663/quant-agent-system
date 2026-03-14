# quant_agent_system/data/sync_service.py
import os
import sys
import json
import logging
import duckdb
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_config import SYNC_TABLES_CONFIG, UPDATE_INTERVALS, MAX_STOCKS_PER_SYNC
from watched_stocks import WatchedStocksManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "db/quant_data.duckdb")


class SyncService:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self.watched_stocks = WatchedStocksManager(self.db_path)
        self._ensure_sync_logs_table()
    
    def _ensure_sync_logs_table(self):
        """确保同步日志表存在"""
        conn = duckdb.connect(self.db_path, read_only=False)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                tables_sync TEXT,
                stocks_updated INTEGER,
                status VARCHAR,
                error_message TEXT
            )
        """)
        conn.close()
    
    def trigger_sync(self, tables: List[str] = None) -> Dict:
        """手动触发同步"""
        start_time = datetime.now()
        logger.info(f"开始同步任务 (tables: {tables or 'all'})")
        
        tables_to_sync = tables or list(SYNC_TABLES_CONFIG.keys())
        total_stocks = 0
        errors = []
        
        watched = self.watched_stocks.get_tickers()
        hot = self.watched_stocks.get_hot_stocks()
        
        all_stocks = list(set(watched + hot))[:MAX_STOCKS_PER_SYNC]
        
        for table in tables_to_sync:
            try:
                count = self._sync_table(table, all_stocks)
                total_stocks += count
                logger.info(f"表 {table} 同步完成: {count} 条")
            except Exception as e:
                error_msg = f"{table}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"表 {table} 同步失败: {e}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        status = "success" if not errors else "partial"
        error_msg = "; ".join(errors) if errors else None
        
        self._log_sync(
            start_time=start_time,
            end_time=end_time,
            tables=tables_to_sync,
            stocks_updated=total_stocks,
            status=status,
            error_message=error_msg
        )
        
        result = {
            "status": status,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "tables_sync": tables_to_sync,
            "stocks_updated": total_stocks,
            "errors": errors
        }
        
        logger.info(f"同步完成: {result}")
        return result
    
    def _sync_table(self, table: str, stocks: List[str]) -> int:
        """同步单个表"""
        try:
            from core.redis_bus import RedisBus
            redis_bus = RedisBus()
        except Exception as e:
            logger.warning(f"Redis 不可用，跳过实际同步: {e}")
            return 0
        
        count = 0
        
        for ticker in stocks:
            try:
                task = {
                    "task_id": f"sync_{table}_{ticker}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "ticker": ticker,
                    "table": table
                }
                redis_bus.add_to_stream("data_fetch_queue", task)
                count += 1
            except Exception as e:
                logger.warning(f"添加同步任务失败 {ticker}: {e}")
        
        return count
    
    def _log_sync(self, start_time: datetime, end_time: datetime, 
                  tables: List[str], stocks_updated: int, 
                  status: str, error_message: str = None):
        """记录同步日志"""
        conn = duckdb.connect(self.db_path, read_only=False)
        
        # 获取下一个ID
        result = conn.execute("SELECT MAX(id) FROM sync_logs").fetchone()
        next_id = (result[0] or 0) + 1
        
        conn.execute("""
            INSERT INTO sync_logs (id, start_time, end_time, tables_sync, stocks_updated, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            next_id,
            start_time.isoformat(),
            end_time.isoformat(),
            json.dumps(tables),
            stocks_updated,
            status,
            error_message
        ))
        conn.close()
    
    def get_status(self) -> Dict:
        """获取同步状态"""
        conn = duckdb.connect(self.db_path, read_only=True)
        
        last_sync = conn.execute("""
            SELECT * FROM sync_logs 
            ORDER BY id DESC 
            LIMIT 1
        """).fetchone()
        
        watched_count = conn.execute("SELECT COUNT(*) FROM watched_stocks").fetchone()[0]
        
        conn.close()
        
        return {
            "last_sync": {
                "id": last_sync[0] if last_sync else None,
                "start_time": last_sync[1] if last_sync else None,
                "end_time": last_sync[2] if last_sync else None,
                "tables": json.loads(last_sync[3]) if last_sync and last_sync[3] else [],
                "stocks_updated": last_sync[4] if last_sync else 0,
                "status": last_sync[5] if last_sync else None,
                "error": last_sync[6] if last_sync else None
            },
            "watched_stocks_count": watched_count,
            "sync_enabled": True
        }
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """获取同步日志"""
        conn = duckdb.connect(self.db_path, read_only=True)
        logs = conn.execute(f"""
            SELECT * FROM sync_logs 
            ORDER BY id DESC 
            LIMIT {limit}
        """).fetchall()
        conn.close()
        
        return [
            {
                "id": l[0],
                "start_time": l[1],
                "end_time": l[2],
                "tables": json.loads(l[3]) if l[3] else [],
                "stocks_updated": l[4],
                "status": l[5],
                "error": l[6]
            }
            for l in logs
        ]


if __name__ == "__main__":
    svc = SyncService()
    result = svc.trigger_sync()
    print(json.dumps(result, indent=2, ensure_ascii=False))

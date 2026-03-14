# quant_agent_system/data/watched_stocks.py
import os
import sys
import duckdb
import logging
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sync_config import HOT_STOCKS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "db/quant_data.duckdb")


class WatchedStocksManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self._ensure_table()
    
    def _ensure_table(self):
        """确保关注股票表存在"""
        conn = duckdb.connect(self.db_path, read_only=False)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS watched_stocks (
                ticker VARCHAR PRIMARY KEY,
                name VARCHAR,
                added_date DATE,
                source VARCHAR DEFAULT 'user'
            )
        """)
        conn.close()
        logger.info("watched_stocks 表初始化完成")
    
    def add_stock(self, ticker: str, name: str = None, source: str = 'user') -> bool:
        """添加关注股票"""
        ticker = ticker.strip().zfill(6)
        conn = duckdb.connect(self.db_path, read_only=False)
        try:
            conn.execute("""
                INSERT OR REPLACE INTO watched_stocks (ticker, name, added_date, source)
                VALUES (?, ?, ?, ?)
            """, (ticker, name, datetime.now().strftime("%Y-%m-%d"), source))
            conn.close()
            logger.info(f"添加关注股票: {ticker} ({name})")
            return True
        except Exception as e:
            logger.error(f"添加关注股票失败: {e}")
            conn.close()
            return False
    
    def remove_stock(self, ticker: str) -> bool:
        """删除关注股票"""
        ticker = ticker.strip().zfill(6)
        conn = duckdb.connect(self.db_path, read_only=False)
        try:
            conn.execute("DELETE FROM watched_stocks WHERE ticker = ?", (ticker,))
            conn.close()
            logger.info(f"删除关注股票: {ticker}")
            return True
        except Exception as e:
            logger.error(f"删除关注股票失败: {e}")
            conn.close()
            return False
    
    def get_all(self) -> List[Dict]:
        """获取所有关注股票"""
        conn = duckdb.connect(self.db_path, read_only=True)
        result = conn.execute("""
            SELECT ticker, name, added_date, source 
            FROM watched_stocks 
            ORDER BY source DESC, added_date DESC
        """).fetchall()
        conn.close()
        return [
            {"ticker": r[0], "name": r[1], "added_date": r[2], "source": r[3]}
            for r in result
        ]
    
    def get_tickers(self) -> List[str]:
        """获取所有关注股票代码"""
        conn = duckdb.connect(self.db_path, read_only=True)
        result = conn.execute("SELECT ticker FROM watched_stocks").fetchall()
        conn.close()
        return [r[0] for r in result]
    
    def get_hot_stocks(self) -> List[str]:
        """获取热门股票代码"""
        return HOT_STOCKS.copy()
    
    def init_hot_stocks(self) -> int:
        """初始化热门股票池"""
        conn = duckdb.connect(self.db_path, read_only=False)
        count = 0
        for ticker in HOT_STOCKS:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO watched_stocks (ticker, name, added_date, source)
                    VALUES (?, ?, ?, ?)
                """, (ticker, None, datetime.now().strftime("%Y-%m-%d"), 'hot'))
                count += 1
            except Exception:
                pass
        conn.close()
        logger.info(f"初始化热门股票池完成: {count} 只")
        return count
    
    def is_watched(self, ticker: str) -> bool:
        """检查是否已关注"""
        ticker = ticker.strip().zfill(6)
        conn = duckdb.connect(self.db_path, read_only=True)
        result = conn.execute(
            "SELECT 1 FROM watched_stocks WHERE ticker = ?", (ticker,)
        ).fetchone()
        conn.close()
        return result is not None
    
    def count(self) -> int:
        """获取关注股票数量"""
        conn = duckdb.connect(self.db_path, read_only=True)
        result = conn.execute("SELECT COUNT(*) FROM watched_stocks").fetchone()
        conn.close()
        return result[0] if result else 0


if __name__ == "__main__":
    mgr = WatchedStocksManager()
    print(f"当前关注: {mgr.count()} 只")
    print(f"热门股票: {len(mgr.get_hot_stocks())} 只")

# 数据库定期同步服务实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 quant_agent_system 增加定时/手动触发数据库同步功能，确保本地数据库即时有效

**Architecture:** 创建独立同步服务模块，包含调度器、关注股票管理、同步逻辑，集成到现有 API Server

**Tech Stack:** APScheduler, DuckDB, Redis, Flask

---

## 文件结构

```
quant_agent_system/
├── data/
│   ├── sync_config.py          # 新增: 同步配置
│   ├── watched_stocks.py        # 新增: 关注股票管理
│   ├── sync_scheduler.py        # 新增: APScheduler 调度器
│   ├── sync_service.py          # 新增: 同步服务主入口
│   └── init_db.py              # 修改: 添加 sync_logs 表
└── web_ui/backend/
    └── api_server.py           # 修改: 添加同步API端点
```

---

## Chunk 1: 基础组件 (配置 + 关注股票管理)

### Task 1: 创建同步配置文件

**Files:**
- Create: `quant_agent_system/data/sync_config.py`

- [ ] **Step 1: 创建 sync_config.py**

```python
# quant_agent_system/data/sync_config.py
import os
from datetime import datetime

# 各数据表的更新频率配置
SYNC_TABLES_CONFIG = {
    "market_daily_qfq": {
        "frequency": "daily",
        "priority": 1,
        "description": "股票日线行情"
    },
    "daily_valuation_metrics": {
        "frequency": "daily", 
        "priority": 2,
        "description": "每日估值指标"
    },
    "industry_daily": {
        "frequency": "daily",
        "priority": 1,
        "description": "行业指数每日行情"
    },
    "financial_statements": {
        "frequency": "quarterly",
        "priority": 3,
        "description": "财务报表"
    },
    "sentiment_score": {
        "frequency": "daily",
        "priority": 4,
        "description": "舆情评分"
    },
    "catalyst_events": {
        "frequency": "daily",
        "priority": 5,
        "description": "事件催化"
    },
}

# 更新周期 (天数)
UPDATE_INTERVALS = {
    "market_daily_qfq": 1,
    "daily_valuation_metrics": 1,
    "industry_daily": 1,
    "financial_statements": 90,
    "sentiment_score": 1,
    "catalyst_events": 1,
}

# 全局同步配置
DEFAULT_SYNC_INTERVAL_HOURS = int(os.getenv("SYNC_INTERVAL_HOURS", "6"))
SYNC_ENABLED = os.getenv("SYNC_ENABLED", "true").lower() == "true"
MAX_STOCKS_PER_SYNC = int(os.getenv("MAX_STOCKS_PER_SYNC", "50"))
SYNC_TIMEOUT_SECONDS = int(os.getenv("SYNC_TIMEOUT_SECONDS", "300"))

# 热门股票池 (100只A股)
HOT_STOCKS = [
    "000001", "000002", "000004", "000005", "000006", "000007", "000008", "000009",
    "000010", "000011", "000012", "000014", "000016", "000017", "000018", "000019",
    "000020", "000021", "000022", "000023", "000025", "000026", "000027", "000028",
    "000029", "000030", "000031", "000032", "000033", "000034", "000035", "000036",
    "000037", "000038", "000039", "000040", "000042", "000043", "000045", "000046",
    "000048", "000049", "000050", "000055", "000056", "000058", "000059", "000060",
    "000061", "000062", "000063", "000065", "000066", "000068", "000069", "000070",
    "000078", "000088", "000089", "000090", "000096", "000099", "000100", "000150",
    "000151", "000152", "000153", "000155", "000156", "000157", "000158", "000159",
    "000166", "000301", "000333", "000338", "000400", "000401", "000402", "000403",
    "000404", "000410", "000415", "000416", "000417", "000418", "000419", "000420",
    "000421", "000422", "000423", "000425", "000426", "000428", "000429", "000430",
    "000488", "000498", "000501", "000502", "000503", "000505", "000506", "000507",
    "000516", "000517", "000518", "000519", "000521", "000525", "000526", "000528"
]
```

- [ ] **Step 2: 提交变更**

---

### Task 2: 创建关注股票管理模块

**Files:**
- Create: `quant_agent_system/data/watched_stocks.py`

- [ ] **Step 1: 创建 watched_stocks.py**

```python
# quant_agent_system/data/watched_stocks.py
import os
import duckdb
import logging
from datetime import datetime
from typing import List, Dict, Optional

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
```

- [ ] **Step 2: 测试 watched_stocks 模块**

```bash
cd /home/jianwei/financial/quant_agent_system
python -c "
from data.watched_stocks import WatchedStocksManager
mgr = WatchedStocksManager()
print(f'当前关注: {mgr.count()}')
mgr.init_hot_stocks()
print(f'初始化后: {mgr.count()}')
stocks = mgr.get_tickers()
print(f'前5只: {stocks[:5]}')
"
```

- [ ] **Step 3: 提交变更**

---

## Chunk 2: 同步调度器 + 服务主入口

### Task 3: 创建同步调度器

**Files:**
- Create: `quant_agent_system/data/sync_scheduler.py`

- [ ] **Step 1: 创建 sync_scheduler.py**

```python
# quant_agent_system/data/sync_scheduler.py
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
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
```

- [ ] **Step 2: 测试调度器 (模拟)**

```bash
cd /home/jianwei/financial/quant_agent_system
python -c "
from data.sync_scheduler import SyncScheduler
print('调度器模块导入成功')
"
```

---

### Task 4: 创建同步服务主入口

**Files:**
- Create: `quant_agent_system/data/sync_service.py`

- [ ] **Step 1: 创建 sync_service.py**

```python
# quant_agent_system/data/sync_service.py
import os
import json
import logging
import duckdb
from datetime import datetime
from typing import Dict, List, Optional

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
        
        # 获取需要同步的股票
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
        
        # 记录同步日志
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
        from core.redis_bus import RedisBus
        
        redis_bus = RedisBus()
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
        conn.execute("""
            INSERT INTO sync_logs (start_time, end_time, tables_sync, stocks_updated, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
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
```

- [ ] **Step 2: 测试同步服务**

```bash
cd /home/jianwei/financial/quant_agent_system
python -c "
from data.sync_service import SyncService
svc = SyncService()
status = svc.get_status()
print(json.dumps(status, indent=2, ensure_ascii=False))
"
```

- [ ] **Step 3: 提交变更**

---

## Chunk 3: API 端点集成

### Task 5: 扩展 API Server

**Files:**
- Modify: `quant_agent_system/web_ui/backend/api_server.py`

- [ ] **Step 1: 添加同步相关 import 和端点**

在 api_server.py 文件末尾添加:

```python
# ====== 同步管理 API ======
from data.sync_service import SyncService
from data.sync_scheduler import SyncScheduler
from data.watched_stocks import WatchedStocksManager
import threading

sync_service = SyncService()
sync_scheduler = SyncScheduler(sync_service)
scheduler_thread = None

def start_scheduler_background():
    """后台启动调度器"""
    global scheduler_thread
    if not sync_scheduler.is_running():
        scheduler_thread = threading.Thread(target=sync_scheduler.start, daemon=True)
        scheduler_thread.start()

@app.route('/api/sync/trigger', methods=['POST'])
def trigger_sync():
    """手动触发同步"""
    try:
        data = request.get_json() or {}
        tables = data.get('tables')
        result = sync_service.trigger_sync(tables)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sync/status', methods=['GET'])
def get_sync_status():
    """获取同步状态"""
    try:
        status = sync_service.get_status()
        status['scheduler_running'] = sync_scheduler.is_running()
        status['next_run'] = sync_scheduler.get_next_run()
        return jsonify({"success": True, "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sync/logs', methods=['GET'])
def get_sync_logs():
    """获取同步日志"""
    try:
        limit = request.args.get('limit', 100, type=int)
        logs = sync_service.get_logs(limit)
        return jsonify({"success": True, "data": logs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ====== 关注股票管理 API ======
watched_stocks_manager = WatchedStocksManager()

@app.route('/api/stocks/watched', methods=['GET'])
def get_watched_stocks():
    """获取关注股票列表"""
    try:
        stocks = watched_stocks_manager.get_all()
        return jsonify({"success": True, "data": stocks})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stocks/watched', methods=['POST'])
def add_watched_stock():
    """添加关注股票"""
    try:
        data = request.get_json()
        ticker = data.get('ticker')
        name = data.get('name')
        if not ticker:
            return jsonify({"success": False, "error": "缺少 ticker"}), 400
        
        success = watched_stocks_manager.add_stock(ticker, name, 'user')
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stocks/watched/<ticker>', methods=['DELETE'])
def remove_watched_stock(ticker):
    """删除关注股票"""
    try:
        success = watched_stocks_manager.remove_stock(ticker)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stocks/watched/init-hot', methods=['POST'])
def init_hot_stocks():
    """初始化热门股票池"""
    try:
        count = watched_stocks_manager.init_hot_stocks()
        return jsonify({"success": True, "count": count})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

- [ ] **Step 2: 在应用启动时初始化调度器**

找到 `if __name__ == "__main__":` 块，添加:

```python
# 启动时自动初始化热门股票和调度器
try:
    watched_stocks_manager.init_hot_stocks()
    start_scheduler_background()
except Exception as e:
    print(f"同步服务初始化警告: {e}")
```

- [ ] **Step 3: 测试 API 端点**

```bash
cd /home/jianwei/financial/quant_agent_system
# 启动 API Server 测试
python -c "
from web_ui.backend.api_server import app
client = app.test_client()

# 测试获取同步状态
resp = client.get('/api/sync/status')
print('GET /api/sync/status:', resp.status_code, resp.json)

# 测试获取关注股票
resp = client.get('/api/stocks/watched')
print('GET /api/stocks/watched:', resp.status_code, resp.json)
"
```

- [ ] **Step 4: 提交变更**

---

## Chunk 4: 更新数据库初始化脚本

### Task 6: 更新 init_db.py

**Files:**
- Modify: `quant_agent_system/data/init_db.py`

- [ ] **Step 1: 添加 sync_logs 表**

在 init_db.py 的索引创建之前添加:

```python
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                tables_sync TEXT,
                stocks_updated INTEGER,
                status VARCHAR,
                error_message TEXT
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS watched_stocks (
                ticker VARCHAR PRIMARY KEY,
                name VARCHAR,
                added_date DATE,
                source VARCHAR DEFAULT 'user'
            );
        """)
```

- [ ] **Step 2: 提交变更**

---

## 实现完成检查清单

- [ ] Task 1: sync_config.py 创建完成
- [ ] Task 2: watched_stocks.py 创建完成 + 测试通过
- [ ] Task 3: sync_scheduler.py 创建完成
- [ ] Task 4: sync_service.py 创建完成 + 测试通过
- [ ] Task 5: api_server.py 端点添加完成 + 测试通过
- [ ] Task 6: init_db.py 更新完成

---

## 启动方式

```bash
# 方式1: 独立启动同步服务
python quant_agent_system/data/sync_service.py

# 方式2: 启动 API Server (包含同步功能)
python quant_agent_system/web_ui/backend/api_server.py
```

## API 使用示例

```bash
# 手动触发同步
curl -X POST http://localhost:5000/api/sync/trigger

# 获取同步状态
curl http://localhost:5000/api/sync/status

# 获取同步日志
curl http://localhost:5000/api/sync/logs

# 获取关注股票
curl http://localhost:5000/api/stocks/watched

# 添加关注股票
curl -X POST http://localhost:5000/api/stocks/watched \
  -H "Content-Type: application/json" \
  -d '{"ticker": "000001", "name": "平安银行"}'

# 删除关注股票
curl -X DELETE http://localhost:5000/api/stocks/watched/000001

# 初始化热门股票池
curl -X POST http://localhost:5000/api/stocks/watched/init-hot
```

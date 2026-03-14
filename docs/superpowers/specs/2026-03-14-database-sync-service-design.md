# 数据库定期同步服务设计

## 1. 需求概述

为 quant_agent_system 增加定期初始化和更新本地数据库功能，确保本地数据库即时、有效。

### 核心需求
1. **定时自动同步** - 后台进程按设定频率自动更新数据
2. **手动触发同步** - Web UI 按钮触发同步
3. **增量更新** - 只更新热门股票和用户关注的股票
4. **用户关注股票管理** - Web UI 添加/删除关注股票

## 2. 技术架构

### 组件结构
```
quant_agent_system/
├── data/
│   ├── sync_service.py          # 同步调度主服务
│   ├── sync_scheduler.py        # APScheduler 调度器
│   ├── sync_config.py           # 同步配置
│   ├── watched_stocks.py        # 关注股票管理
│   └── workers/
│       ├── tushare_fetcher.py   # 已有
│       ├── akshare_fetcher.py   # 已有
│       └── data_writer_worker.py # 已有
└── web_ui/backend/
    └── api_server.py            # 扩展同步API端点
```

### 数据流程
```
定时触发 / 手动触发
       ↓
  同步调度器 (sync_scheduler)
       ↓
  获取关注股票列表 (watched_stocks)
       ↓
  数据获取 Workers (并行)
       ↓
  数据写入 (data_writer)
       ↓
  更新同步状态和日志
```

## 3. 功能设计

### 3.1 同步配置 (sync_config.py)

```python
SYNC_CONFIG = {
    # 各数据表的更新频率配置
    "market_daily_qfq": {"frequency": "daily", "priority": 1},
    "daily_valuation_metrics": {"frequency": "daily", "priority": 2},
    "industry_daily": {"frequency": "daily", "priority": 1},
    "financial_statements": {"frequency": "quarterly", "priority": 3},
    "sentiment_score": {"frequency": "daily", "priority": 4},
    "catalyst_events": {"frequency": "daily", "priority": 5},
}

# 全局同步间隔配置
DEFAULT_SYNC_INTERVAL = 6  # 小时
```

### 3.2 关注股票管理 (watched_stocks.py)

```python
# 热门股票池 (100只)
HOT_STOCKS = [
    "000001", "000002", "000004", "000005", ...  # 平安银行等
]

class WatchedStocksManager:
    def __init__(self):
        self.db_path = "data/db/quant_data.duckdb"
        self._ensure_table()
    
    def _ensure_table(self):
        # 创建 watched_stocks 表
        conn = duckdb.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS watched_stocks (
                ticker VARCHAR PRIMARY KEY,
                name VARCHAR,
                added_date DATE,
                source VARCHAR DEFAULT 'user'  -- 'user' or 'hot'
            )
        """)
        conn.close()
    
    def add_stock(self, ticker, name=None, source='user'):
        # 添加关注股票
    
    def remove_stock(self, ticker):
        # 删除关注股票
    
    def get_all(self):
        # 获取所有关注股票
    
    def init_hot_stocks(self):
        # 初始化热门股票池
```

### 3.3 同步调度器 (sync_scheduler.py)

```python
from apscheduler.schedulers.background import BackgroundScheduler

class SyncScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.config = SYNC_CONFIG
    
    def start(self, interval_hours=6):
        # 添加定时同步任务
        self.scheduler.add_job(
            self.sync_all,
            'interval',
            hours=interval_hours,
            id='db_sync'
        )
        self.scheduler.start()
    
    def sync_all(self):
        # 执行全量同步
    
    def sync_table(self, table_name):
        # 同步指定表
```

### 3.4 同步服务主入口 (sync_service.py)

```python
class SyncService:
    def __init__(self):
        self.watched_stocks = WatchedStocksManager()
        self.scheduler = SyncScheduler()
        self.redis_bus = RedisBus()
    
    def start(self):
        # 启动定时调度
        self.scheduler.start()
    
    def trigger_sync(self, tables=None):
        # 手动触发同步
    
    def get_status(self):
        # 获取同步状态
    
    def get_logs(self, limit=100):
        # 获取同步日志
```

## 4. API 端点设计

### 4.1 同步管理

| 方法 | 路径 | 描述 |
|-----|------|------|
| POST | /api/sync/trigger | 手动触发同步 |
| GET | /api/sync/status | 获取同步状态 |
| GET | /api/sync/logs | 获取同步日志 |

### 4.2 关注股票管理

| 方法 | 路径 | 描述 |
|-----|------|------|
| GET | /api/stocks/watched | 获取关注股票列表 |
| POST | /api/stocks/watched | 添加关注股票 |
| DELETE | /api/stocks/watched/{ticker} | 删除关注股票 |
| POST | /api/stocks/watched/init-hot | 初始化热门股票池 |

## 5. Web UI 集成

### 关注股票管理界面
- 显示当前关注的股票列表
- 添加股票输入框 (支持代码或名称搜索)
- 删除按钮
- 初始化热门股票按钮
- 最后同步时间显示

### 同步控制界面
- 同步状态指示器 (运行中/空闲/错误)
- 手动同步按钮
- 同步间隔设置
- 同步日志查看

## 6. 数据同步策略

### 增量更新逻辑

```python
def get_latest_date(table_name, ticker):
    """获取表中某股票的最新日期"""
    conn = duckdb.connect(DB_PATH, read_only=True)
    result = conn.execute(f"""
        SELECT MAX(trade_date) FROM {table_name}
        WHERE ticker = ?
    """, (ticker,)).fetchone()
    conn.close()
    return result[0] if result else None

def should_update(table_name, ticker):
    """判断是否需要更新"""
    latest = get_latest_date(table_name, ticker)
    if latest is None:
        return True
    # 检查是否超过更新周期
    return (datetime.now() - latest).days >= UPDATE_INTERVALS.get(table_name, 1)
```

### 更新周期配置

| 数据表 | 更新周期 | 保留天数 |
|--------|---------|---------|
| market_daily_qfq | 1天 | 永久 |
| daily_valuation_metrics | 1天 | 永久 |
| industry_daily | 1天 | 永久 |
| financial_statements | 90天 | 永久 |
| sentiment_score | 1天 | 365天 |
| catalyst_events | 1天 | 180天 |

## 7. 错误处理与日志

### 日志表结构

```python
conn.execute("""
    CREATE TABLE IF NOT EXISTS sync_logs (
        id INTEGER PRIMARY KEY,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        tables_sync TEXT,
        stocks_updated INTEGER,
        status VARCHAR,  -- 'success', 'partial', 'failed'
        error_message TEXT
    )
""")
```

### 错误处理策略
1. 单表失败不影响其他表
2. 单股票失败记录日志继续下一个
3. API 超时自动重试 (最多3次)
4. 失败告警通知

## 8. 启动方式

```bash
# 方式1: 独立启动 (推荐)
python data/sync_service.py

# 方式2: 作为API Server的一部分启动
# API Server 启动时自动加载 sync_service
```

## 9. 配置项

```python
# 环境变量配置
SYNC_INTERVAL_HOURS=6          # 同步间隔
SYNC_ENABLED=true              # 是否启用定时同步
MAX_STOCKS_PER_SYNC=50         # 每次同步最多股票数
SYNC_TIMEOUT_SECONDS=300       # 单次同步超时
```

## 10. 实施计划

1. **Phase 1**: 创建基础组件
   - sync_config.py - 配置文件
   - watched_stocks.py - 关注股票管理
   - sync_scheduler.py - 调度器

2. **Phase 2**: 实现同步服务
   - sync_service.py - 主服务
   - 增量更新逻辑

3. **Phase 3**: API 集成
   - 扩展 api_server.py
   - 添加同步相关端点

4. **Phase 4**: Web UI
   - 添加关注股票管理界面
   - 添加同步控制界面

5. **Phase 5**: 测试与优化
   - 单元测试
   - 集成测试
   - 性能优化

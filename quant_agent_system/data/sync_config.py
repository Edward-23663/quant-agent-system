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

# data/workers/tushare_fetcher.py
import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import tushare as ts
import akshare as ak
from core.redis_bus import RedisBus

# Load environment variables
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

CURRENT_DATE = datetime.now().strftime("%Y%m%d")
CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().month

logging.basicConfig(level=logging.INFO, format='%(asctime)s - TUSHARE_FETCHER - %(message)s')

class TushareFetcherWorker:
    def __init__(self):
        self.redis_bus = RedisBus()
        self.fetch_queue = "data_fetch_queue"
        self.use_akshare = False
        
        # Try initialize Tushare
        token = os.getenv("TUSHARE_TOKEN", "")
        if token:
            try:
                ts.set_token(token)
                self.pro = ts.pro_api()
                # Test connection
                self.pro.trade_cal(exchange='SSE', start_date='20240101', end_date='20240102')
                logging.info("✅ Tushare Pro API 初始化成功")
            except Exception as e:
                logging.warning(f"⚠️ Tushare API 不可用: {e}，将使用 AkShare 备用")
                self.pro = None
                self.use_akshare = True
        else:
            logging.info("未配置 TUSHARE_TOKEN，将使用 AkShare")
            self.use_akshare = True

    def run(self):
        mode = "AkShare" if self.use_akshare else "Tushare"
        logging.info(f"🌐 数据获取 Worker 启动 (使用: {mode})，监听数据采集指令...")
        while True:
            task = self.redis_bus.pop_from_queue(self.fetch_queue, timeout=0)
            if task:
                self._process_task(task)

    def _process_task(self, task: dict):
        task_id = task.get('task_id', 'unknown')
        ticker = task.get('ticker')
        table = task.get('table')
        
        self.redis_bus.publish_status(task_id, f"📥 收到采集指令: 正在获取 {ticker} 的 {table} 数据...")
        
        try:
            df = self._fetch_data(ticker, table)
            
            if df is None or df.empty:
                raise ValueError("数据源返回空数据")

            df = self._clean_data(df, table)
            
            write_payload = {
                "task_id": task_id,
                "table": table,
                "data": json.dumps(df.to_dict(orient='records'))
            }
            self.redis_bus.add_to_stream("db_write_stream", write_payload)
            self.redis_bus.publish_status(task_id, f"📤 {table} 数据已推送落盘流")
            
            time.sleep(1.5)

        except Exception as e:
            logging.error(f"采集失败: {e}")
            self.redis_bus.publish_status(task_id, f"❌ 数据采集失败: {e}")

    def _fetch_data(self, ticker: str, table: str):
        if not self.use_akshare and self.pro:
            try:
                return self._fetch_from_tushare(ticker, table)
            except Exception as e:
                logging.warning(f"Tushare 失败: {e}，切换到 AkShare")
                self.use_akshare = True
        
        return self._fetch_from_akshare(ticker, table)
    
    def _fetch_from_tushare(self, ticker: str, table: str):
        ts_code = f"{ticker}.SZ" if not ticker.endswith(('.SZ', '.SH')) else ticker
        
        if table == "market_daily_qfq":
            start_date = f"{CURRENT_YEAR-3}0101"
            return self.pro.daily(ts_code=ts_code, start_date=start_date)
        elif table == "daily_valuation_metrics":
            start_date = f"{CURRENT_YEAR-3}0101"
            return self.pro.daily_basic(ts_code=ts_code, start_date=start_date)
        elif table == "financial_statements":
            return self.pro.income(ts_code=ts_code, limit=20)
        elif table == "stock_basic":
            return self.pro.stock_basic(exchange='', list_status='L')
        
        raise ValueError(f"未知表: {table}")
    
    def _fetch_from_akshare(self, ticker: str, table: str):
        if table == "market_daily_qfq":
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = f"{datetime.now().year-3}0101"
            return ak.stock_zh_a_hist(symbol=ticker, start_date=start_date, end_date=end_date)
        elif table == "stock_basic":
            return ak.stock_info_a_code_name()
        elif table == "financial_statements":
            return ak.stock_financial_analysis_indicator(symbol=ticker)
        
        # Fallback to mock data
        return self._fetch_mock_data(ticker, table)
    
    def _fetch_mock_data(self, ticker: str, table: str):
        from datetime import date, timedelta
        
        today = datetime.now().date()
        
        if table == "market_daily_qfq":
            data = []
            for i in range(250):
                d = today - timedelta(days=i)
                data.append({
                    'ticker': ticker,
                    'trade_date': d.strftime('%Y-%m-%d'),
                    'open_qfq': 12.0 + i * 0.01,
                    'high_qfq': 12.5 + i * 0.01,
                    'low_qfq': 11.5 + i * 0.01,
                    'close_qfq': 12.0 + i * 0.01,
                    'volume': 1000000.0,
                    'amount': 12000000.0
                })
            return pd.DataFrame(data)
            
        return None

    def _clean_data(self, df: pd.DataFrame, table: str) -> pd.DataFrame:
        if df is None or df.empty:
            return df
            
        # Handle both Tushare and AkShare column names
        rename_map = {
            'ts_code': 'ticker',
            'trade_date': 'trade_date',
            'ann_date': 'announce_date',
            'end_date': 'report_date',
            'open': 'open_qfq',
            'close': 'close_qfq',
            'high': 'high_qfq',
            'low': 'low_qfq',
            'vol': 'volume',
            '日期': 'trade_date',
            '股票代码': 'ticker',
            '开盘': 'open_qfq',
            '收盘': 'close_qfq',
            '最高': 'high_qfq',
            '最低': 'low_qfq',
            '成交量': 'volume',
            '成交额': 'amount',
        }
        
        df = df.rename(columns=rename_map)
        
        # Convert ts_code to simple ticker
        if 'ticker' in df.columns and df['ticker'].dtype == object:
            df['ticker'] = df['ticker'].astype(str).str.replace('.SZ', '').str.replace('.SH', '')
        
        # Convert date columns
        date_cols = ['trade_date', 'announce_date', 'report_date', 'list_date']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # Keep only required columns
        required_cols = {
            'market_daily_qfq': ['ticker', 'trade_date', 'open_qfq', 'high_qfq', 'low_qfq', 'close_qfq', 'volume', 'amount'],
            'daily_valuation_metrics': ['ticker', 'trade_date', 'pe', 'pb', 'ps', 'total_mv'],
            'stock_basic': ['ticker', 'name', 'industry', 'list_date'],
            'financial_statements': ['ticker', 'announce_date', 'report_date', 'total_revenue', 'net_profit', 'free_cash_flow']
        }
        
        cols_to_keep = required_cols.get(table, [])
        df = df[[c for c in cols_to_keep if c in df.columns]]
        
        df = df.fillna(0)
        return df

if __name__ == "__main__":
    TushareFetcherWorker().run()

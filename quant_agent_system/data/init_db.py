import os
import duckdb
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - DB_INIT - %(message)s')

def init_database():
    db_dir = "data/db"
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "quant_data.duckdb")
    
    conn = duckdb.connect(db_path, read_only=False)
    
    try:
        logging.info("开始初始化 DuckDB 量化数据库...")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS financial_statements (
                ticker VARCHAR,
                announce_date DATE,
                report_date DATE,
                total_revenue DOUBLE,
                net_profit DOUBLE,
                free_cash_flow DOUBLE,
                total_assets DOUBLE,
                total_liabilities DOUBLE,
                total_equity DOUBLE,
                PRIMARY KEY (ticker, announce_date, report_date)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS market_daily_qfq (
                ticker VARCHAR,
                trade_date DATE,
                open_qfq DOUBLE,
                high_qfq DOUBLE,
                low_qfq DOUBLE,
                close_qfq DOUBLE,
                volume DOUBLE,
                amount DOUBLE,
                PRIMARY KEY (ticker, trade_date)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_valuation_metrics (
                ticker VARCHAR,
                trade_date DATE,
                pe_ttm DOUBLE,
                pb DOUBLE,
                ps_ttm DOUBLE,
                total_mv DOUBLE,
                PRIMARY KEY (ticker, trade_date)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS stock_basic (
                ticker VARCHAR PRIMARY KEY,
                name VARCHAR,
                industry VARCHAR,
                list_date DATE,
                market VARCHAR,
                exchange VARCHAR
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS valuation_results (
                ticker VARCHAR,
                valuation_date DATE,
                dcf_value DOUBLE,
                pe_value DOUBLE,
                pb_value DOUBLE,
                ps_value DOUBLE,
                PRIMARY KEY (ticker, valuation_date)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS fundamental_health_score (
                ticker VARCHAR,
                calc_date DATE,
                health_score DOUBLE,
                roe DOUBLE,
                debt_ratio DOUBLE,
                current_ratio DOUBLE,
                net_profit_margin DOUBLE,
                PRIMARY KEY (ticker, calc_date)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS fundamental_metrics (
                ticker VARCHAR,
                report_date DATE,
                pe_ttm DOUBLE,
                pb DOUBLE,
                roe DOUBLE,
                PRIMARY KEY (ticker, report_date)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sentiment_score (
                ticker VARCHAR,
                calc_date DATE,
                sentiment_score DOUBLE,
                polarity DOUBLE,
                heat_index DOUBLE,
                PRIMARY KEY (ticker, calc_date)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS news_sentiment (
                id INTEGER PRIMARY KEY,
                ticker VARCHAR,
                news_date DATE,
                title VARCHAR,
                content VARCHAR,
                sentiment_score DOUBLE,
                polarity DOUBLE
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS industry_position (
                ticker VARCHAR,
                calc_date DATE,
                industry VARCHAR,
                relative_strength DOUBLE,
                rotation_phase VARCHAR,
                PRIMARY KEY (ticker, calc_date)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS industry_daily (
                industry VARCHAR,
                trade_date DATE,
                index_value DOUBLE,
                change_pct DOUBLE,
                volume DOUBLE,
                PRIMARY KEY (industry, trade_date)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS industry_valuation (
                industry VARCHAR,
                trade_date DATE,
                pe DOUBLE,
                pb DOUBLE,
                avg_market_cap DOUBLE,
                PRIMARY KEY (industry, trade_date)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS catalyst_events (
                id INTEGER PRIMARY KEY,
                ticker VARCHAR,
                event_date DATE,
                event_type VARCHAR,
                impact_score DOUBLE,
                description VARCHAR
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS corporate_events (
                ticker VARCHAR,
                event_date DATE,
                event_type VARCHAR,
                impact_score DOUBLE,
                description VARCHAR,
                PRIMARY KEY (ticker, event_date, event_type)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS valuation_daily (
                ticker VARCHAR,
                trade_date DATE,
                dcf_value DOUBLE,
                pe_value DOUBLE,
                pb_value DOUBLE,
                PRIMARY KEY (ticker, trade_date)
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER NOT NULL DEFAULT (NEXTVAL('sync_logs_id_seq')),
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                tables_sync TEXT,
                stocks_updated INTEGER,
                status VARCHAR,
                error_message TEXT
            );
        """)
        
        # 创建序列
        conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS sync_logs_id_seq START 1
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS watched_stocks (
                ticker VARCHAR PRIMARY KEY,
                name VARCHAR,
                added_date DATE,
                source VARCHAR DEFAULT 'user'
            );
        """)

        conn.execute("CREATE INDEX IF NOT EXISTS idx_fin_ticker_date ON financial_statements(ticker, announce_date);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mkt_ticker_date ON market_daily_qfq(ticker, trade_date);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_val_ticker_date ON valuation_results(ticker, valuation_date);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sent_ticker_date ON sentiment_score(ticker, calc_date);")
        
        logging.info("✅ DuckDB 表结构与索引初始化完成！")
        
    except Exception as e:
        logging.error(f"数据库初始化失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()

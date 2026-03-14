import os, json, duckdb
import numpy as np

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
        "data/db/quant_data.duckdb"
    )
    db = duckdb.connect(db_path, read_only=True)
    query = "SELECT amount FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 60"
    df = db.execute(query, (ticker, target_date)).df()
    db.close()
    
    if len(df) < 20:
        raise ValueError("DATA_MISSING: 缺乏成交额数据")
    
    amounts = df['amount'].values
    
    avg_vol_20d = np.mean(amounts[:20])
    avg_vol_60d = np.mean(amounts)
    
    liquidity_ratio = avg_vol_20d / (avg_vol_60d + 1e-5)
    
    is_drying_up = liquidity_ratio < 0.5 

    print(json.dumps({
        "avg_amount_20d": round(avg_vol_20d, 2),
        "liquidity_trend_ratio": round(liquidity_ratio, 2),
        "is_liquidity_drying_up": bool(is_drying_up),
        "liquidity_status": "流动性枯竭警报" if is_drying_up else "流动性充裕"
    }))

if __name__ == "__main__": main()

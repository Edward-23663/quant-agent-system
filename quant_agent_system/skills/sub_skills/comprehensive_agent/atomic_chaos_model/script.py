import os, json, duckdb
import numpy as np

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params['ticker']
    target_date = params['target_date']

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    query = "SELECT close_qfq FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 250"
    df = db.execute(query, (ticker, target_date)).df()
    if len(df) < 100: raise ValueError("DATA_MISSING: 数据长度不足以计算 Hurst 指数")
    
    prices = df['close_qfq'].values[::-1]
    
    lags = range(2, 20)
    tau = [np.sqrt(np.std(np.subtract(prices[lag:], prices[:-lag]))) for lag in lags]
    
    poly = np.polyfit(np.log(lags), np.log(tau), 1)
    hurst = poly[0] * 2.0

    if hurst < 0.45: regime = "Mean Reverting (均值回归 - 震荡市)"
    elif hurst > 0.55: regime = "Trending (趋势延续 - 单边市)"
    else: regime = "Random Walk (随机游走 - 混沌无序)"

    print(json.dumps({
        "hurst_exponent": round(float(hurst), 3),
        "market_regime": regime,
        "chaos_advice": "适合高抛低吸" if hurst < 0.45 else ("适合趋势跟踪" if hurst > 0.55 else "不具有统计学可预测性")
    }))

if __name__ == "__main__": main()

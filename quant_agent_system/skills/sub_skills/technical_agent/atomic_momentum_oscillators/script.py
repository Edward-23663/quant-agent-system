import os
import json
import duckdb
import pandas as pd


def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    query = "SELECT trade_date, high_qfq, low_qfq, close_qfq FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 60"
    df = db.execute(query, (ticker, target_date)).df()
    if len(df) < 30:
        raise ValueError("DATA_MISSING: 数据不足计算RSI/KDJ")

    df = df.iloc[::-1].reset_index(drop=True)

    delta = df['close_qfq'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-5)
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]

    rsi_status = "超卖 (Oversold)" if current_rsi < 30 else ("超买 (Overbought)" if current_rsi > 70 else "中性 (Neutral)")

    low_min = df['low_qfq'].rolling(9).min()
    high_max = df['high_qfq'].rolling(9).max()
    rsv = (df['close_qfq'] - low_min) / (high_max - low_min + 1e-5) * 100
    k = rsv.ewm(com=2, adjust=False).mean()
    d = k.ewm(com=2, adjust=False).mean()
    j = 3 * k - 2 * d

    current_k, current_d, current_j = k.iloc[-1], d.iloc[-1], j.iloc[-1]

    kdj_cross = "金叉 (Golden Cross)" if current_k > current_d and k.iloc[-2] <= d.iloc[-2] else \
                "死叉 (Death Cross)" if current_k < current_d and k.iloc[-2] >= d.iloc[-2] else "无交叉"

    print(json.dumps({
        "RSI_14": {"value": round(float(current_rsi), 1), "status": rsi_status},
        "KDJ_9_3_3": {"K": round(float(current_k), 1), "D": round(float(current_d), 1), "J": round(float(current_j), 1), "cross_signal": kdj_cross}
    }))


if __name__ == "__main__":
    main()
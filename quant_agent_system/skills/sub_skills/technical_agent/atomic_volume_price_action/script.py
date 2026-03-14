import os
import json
import duckdb
import pandas as pd


def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    query = "SELECT close_qfq, volume FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 60"
    df = db.execute(query, (ticker, target_date)).df()
    if len(df) < 20:
        raise ValueError("DATA_MISSING: 缺乏成交量数据")

    df = df.iloc[::-1].reset_index(drop=True)

    vol_5 = df['volume'].rolling(5).mean().iloc[-1]
    vol_20 = df['volume'].rolling(20).mean().iloc[-1]
    current_vol = df['volume'].iloc[-1]

    vol_status = "放量 (Volume Expansion)" if current_vol > vol_20 * 1.5 else \
                 "缩量 (Volume Shrinkage)" if current_vol < vol_20 * 0.6 else "平量"

    obv = [0]
    for i in range(1, len(df)):
        if df['close_qfq'].iloc[i] > df['close_qfq'].iloc[i-1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close_qfq'].iloc[i] < df['close_qfq'].iloc[i-1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])

    obv_series = pd.Series(obv)
    obv_ma10 = obv_series.rolling(10).mean().iloc[-1]

    obv_trend = "资金流入 (Accumulation)" if obv_series.iloc[-1] > obv_ma10 else "资金流出 (Distribution)"

    print(json.dumps({
        "volume_action": {"current_vol": float(current_vol), "vol_ma20": float(vol_20), "status": vol_status},
        "OBV_indicator": {"trend": obv_trend, "logic": "OBV线上穿均线代表买盘力量强于卖盘。"}
    }))


if __name__ == "__main__":
    main()
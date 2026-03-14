import os
import json
import duckdb
import pandas as pd


def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    query = "SELECT trade_date, close_qfq FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 100"
    df = db.execute(query, (ticker, target_date)).df()
    if len(df) < 60:
        raise ValueError("DATA_MISSING: 行情数据不足以计算趋势指标")

    df = df.iloc[::-1].reset_index(drop=True)
    close = df['close_qfq']
    current_price = close.iloc[-1]

    ma5 = close.rolling(5).mean().iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]
    ma60 = close.rolling(60).mean().iloc[-1]
    ma_trend = "多头排列 (Bullish)" if current_price > ma5 > ma20 > ma60 else ("空头排列 (Bearish)" if current_price < ma5 < ma20 < ma60 else "震荡交织 (Ranging)")

    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    macd_status = "金叉 (Golden Cross)" if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2] else \
                  "死叉 (Death Cross)" if macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2] else \
                  "多头区间" if histogram.iloc[-1] > 0 else "空头区间"

    std20 = close.rolling(20).std()
    upper_band = ma20 + 2 * std20.iloc[-1]
    lower_band = ma20 - 2 * std20.iloc[-1]

    boll_pos = "突破上轨 (Overbought)" if current_price > upper_band else \
               "跌破下轨 (Oversold)" if current_price < lower_band else "中轨运行"

    print(json.dumps({
        "current_price": float(current_price),
        "ma_system": {"ma5": float(ma5), "ma20": float(ma20), "ma60": float(ma60), "trend": ma_trend},
        "macd_system": {"macd_val": float(macd_line.iloc[-1]), "signal_val": float(signal_line.iloc[-1]), "hist": float(histogram.iloc[-1]), "status": macd_status},
        "boll_system": {"upper": float(upper_band), "mid": float(ma20), "lower": float(lower_band), "position": boll_pos}
    }))


if __name__ == "__main__":
    main()

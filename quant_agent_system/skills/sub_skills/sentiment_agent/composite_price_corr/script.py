import os, json, duckdb

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker", "")
    target_date = params.get("target_date", "")
    sentiment = params.get("sentiment_label", "NEUTRAL")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    query = """
        SELECT trade_date, close_qfq 
        FROM market_daily_qfq 
        WHERE ticker = ? AND trade_date <= ?
        ORDER BY trade_date DESC LIMIT 5
    """
    df = db.execute(query, (ticker, target_date)).df()
    
    if len(df) < 5:
        raise ValueError("DATA_MISSING: 行情数据不足，无法进行时序关联分析")

    current_price = df.iloc[0]['close_qfq']
    price_5d_ago = df.iloc[-1]['close_qfq']
    return_5d = (current_price - price_5d_ago) / price_5d_ago
    
    divergence_flag = False
    analysis = "走势与舆情预期一致。"

    if sentiment == "POSITIVE" and return_5d < -0.03:
        divergence_flag = True
        analysis = "【高危背离】舆情呈现利好，但近5日股价却下跌超过3%。警惕'利好兑现是利空'或主力借利好出货。"
    elif sentiment == "NEGATIVE" and return_5d > 0.03:
        divergence_flag = True
        analysis = "【底背离】舆情极度负面，但股价却逆势上涨超过3%。可能利空已出尽，或有大资金在左侧逆势吸筹。"

    print(json.dumps({
        "price_return_5d_pct": round(float(return_5d) * 100, 2),
        "has_divergence": divergence_flag,
        "correlation_analysis": analysis
    }))

if __name__ == "__main__": main()

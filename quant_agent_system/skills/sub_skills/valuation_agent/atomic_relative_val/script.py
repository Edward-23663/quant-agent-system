import os, json, duckdb
import pandas as pd

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker, target_date = params['ticker'], params['target_date']

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    
    query = """
        SELECT trade_date, pe_ttm, pb 
        FROM daily_valuation_metrics 
        WHERE ticker = ? AND trade_date <= ? 
        ORDER BY trade_date DESC LIMIT 750
    """
    df = db.execute(query, (ticker, target_date)).df()
    if len(df) < 250: raise ValueError("DATA_MISSING: 历史估值数据不足1年")

    current_pe = df.iloc[0]['pe_ttm']
    current_pb = df.iloc[0]['pb']
    
    pe_percentile = (df['pe_ttm'] < current_pe).mean() * 100
    pb_percentile = (df['pb'] < current_pb).mean() * 100

    print(json.dumps({
        "current_pe": float(current_pe), "pe_percentile_3y": round(pe_percentile, 2),
        "current_pb": float(current_pb), "pb_percentile_3y": round(pb_percentile, 2),
        "implied_sentiment": "Undervalued" if pe_percentile < 30 else ("Overvalued" if pe_percentile > 70 else "Fair")
    }))

if __name__ == "__main__": main()

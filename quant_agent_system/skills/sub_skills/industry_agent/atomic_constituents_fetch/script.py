import os, json, duckdb

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    industry = params.get("industry_name")
    target_date = params.get("target_date")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    
    query = """
        SELECT b.ticker, b.name, m.total_mv 
        FROM stock_basic b
        JOIN daily_valuation_metrics m ON b.ticker = m.ticker
        WHERE b.industry = ?
          AND m.trade_date <= ?
        ORDER BY m.trade_date DESC, m.total_mv DESC
        LIMIT 5
    """
    df = db.execute(query, (industry, target_date)).df()
    db.close()
    
    if df.empty:
        raise ValueError("DATA_MISSING: 无法获取该行业的成分股市值数据")
        
    constituents = []
    for _, row in df.iterrows():
        constituents.append({
            "ticker": str(row['ticker']),
            "name": str(row['name']),
            "market_cap_billions": round(float(row['total_mv']) / 10000, 2)
        })

    print(json.dumps({
        "industry": industry,
        "top_5_dragons": constituents
    }))

if __name__ == "__main__": main()

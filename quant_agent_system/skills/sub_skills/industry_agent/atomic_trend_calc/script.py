import os, json, duckdb

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    industry = params.get("industry_name")
    target_date = params.get("target_date")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    
    try:
        query = """
            SELECT trade_date, index_value 
            FROM industry_daily 
            WHERE industry = ? AND trade_date <= ?
            ORDER BY trade_date DESC LIMIT 60
        """
        df = db.execute(query, (industry, target_date)).df()
    except duckdb.CatalogException:
        raise ValueError("DATA_MISSING: 缺失 industry_daily 行业指数表")
    db.close()
        
    if len(df) < 60:
        raise ValueError("DATA_MISSING: 行业历史行情不足 60 天")
        
    df = df.iloc[::-1].reset_index(drop=True)
    
    current_close = df['index_value'].iloc[-1]
    close_20d_ago = df['index_value'].iloc[-20]
    close_60d_ago = df['index_value'].iloc[0]
    
    mom_20d = (current_close - close_20d_ago) / close_20d_ago
    mom_60d = (current_close - close_60d_ago) / close_60d_ago

    print(json.dumps({
        "industry": industry,
        "momentum_20d_pct": round(float(mom_20d) * 100, 2),
        "momentum_60d_pct": round(float(mom_60d) * 100, 2),
        "current_index_val": float(current_close)
    }))

if __name__ == "__main__": main()

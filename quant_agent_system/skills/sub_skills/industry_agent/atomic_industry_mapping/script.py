import os, json, duckdb

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    
    try:
        query = "SELECT industry, name FROM stock_basic WHERE ticker = ?"
        df = db.execute(query, (ticker,)).df()
    except duckdb.CatalogException:
        raise ValueError("DATA_MISSING: 缺失 stock_basic 表")
    db.close()
        
    if df.empty:
        raise ValueError("DATA_MISSING: 未找到该股票的行业映射信息")
        
    row = df.iloc[0]
    
    print(json.dumps({
        "ticker": ticker,
        "stock_name": str(row['name']),
        "industry": str(row['industry']) if row['industry'] else "未知"
    }))

if __name__ == "__main__": main()

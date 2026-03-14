import os, json, duckdb

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    
    query = """
        SELECT report_date, total_revenue, net_profit, free_cash_flow, 
               total_assets, total_liabilities, total_equity 
        FROM financial_statements 
        WHERE ticker = ? AND announce_date <= ?
        ORDER BY report_date DESC LIMIT 1
    """
    df = db.execute(query, (ticker, target_date)).df()
    db.close()
    
    if df.empty:
        raise ValueError("DATA_MISSING: 未找到符合时间条件的财报数据")
        
    row = df.iloc[0]
    
    result = {
        "ticker": ticker,
        "report_date": str(row['report_date']),
        "total_revenue": float(row['total_revenue']),
        "net_profit": float(row['net_profit']),
        "free_cash_flow": float(row['free_cash_flow']),
        "total_assets": float(row['total_assets']),
        "total_liabilities": float(row['total_liabilities']),
        "total_equity": float(row['total_equity'])
    }
    
    print(json.dumps(result))

if __name__ == "__main__": main()

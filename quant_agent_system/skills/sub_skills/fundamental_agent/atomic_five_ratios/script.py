import os, json, duckdb

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    
    query = """
        SELECT report_date, total_revenue, net_profit, total_assets, total_liabilities, total_equity 
        FROM financial_statements 
        WHERE ticker = ? AND announce_date <= ?
        ORDER BY report_date DESC LIMIT 2
    """
    df = db.execute(query, (ticker, target_date)).df()
    db.close()
    
    if len(df) < 2:
        raise ValueError("DATA_MISSING: 历史财报数据不足2期，无法计算比率与增速")
        
    current = df.iloc[0]
    previous = df.iloc[1]
    
    eps = 1e-5
    
    if current['total_equity'] <= 0 or current['total_assets'] <= 0 or current['total_revenue'] <= 0:
        raise ValueError("DATA_INVALID: 财务数据包含无效值(<=0)，无法计算财务比率")
    
    roe = current['net_profit'] / current['total_equity']
    roa = current['net_profit'] / current['total_assets']
    net_margin = current['net_profit'] / current['total_revenue']
    
    debt_to_asset = current['total_liabilities'] / current['total_assets']
    
    rev_growth = (current['total_revenue'] - previous['total_revenue']) / (abs(previous['total_revenue']) + eps)
    
    print(json.dumps({
        "ticker": ticker,
        "report_date": str(current['report_date']),
        "previous_report_date": str(previous['report_date']),
        "roe_pct": round(float(roe) * 100, 2),
        "roa_pct": round(float(roa) * 100, 2),
        "net_profit_margin_pct": round(float(net_margin) * 100, 2),
        "debt_to_asset_pct": round(float(debt_to_asset) * 100, 2),
        "revenue_growth_pct": round(float(rev_growth) * 100, 2)
    }))

if __name__ == "__main__": main()

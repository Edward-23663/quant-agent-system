import os, json, duckdb

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    query = """
        SELECT report_date, net_profit, total_revenue, total_assets, total_equity 
        FROM financial_statements 
        WHERE ticker = ? AND announce_date <= ?
        ORDER BY report_date DESC LIMIT 1
    """
    df = db.execute(query, (ticker, target_date)).df()
    db.close()
    
    if df.empty:
        raise ValueError("DATA_MISSING: 无财报数据")
    
    row = df.iloc[0]
    eps = 1e-5
    
    net_profit_margin = row['net_profit'] / (row['total_revenue'] + eps)
    asset_turnover = row['total_revenue'] / (row['total_assets'] + eps)
    equity_multiplier = row['total_assets'] / (row['total_equity'] + eps)
    
    roe = net_profit_margin * asset_turnover * equity_multiplier

    driver = "均衡型"
    if equity_multiplier > 3.0:
        driver = "高杠杆驱动 (风险较高)"
    elif net_profit_margin > 0.2:
        driver = "高净利驱动 (护城河深)"
    elif asset_turnover > 1.5:
        driver = "高周转驱动 (薄利多销)"

    print(json.dumps({
        "ticker": ticker,
        "report_date": str(row['report_date']),
        "calculated_roe_pct": round(float(roe) * 100, 2),
        "dupont_components": {
            "net_profit_margin": round(float(net_profit_margin), 4),
            "asset_turnover": round(float(asset_turnover), 4),
            "equity_multiplier": round(float(equity_multiplier), 4)
        },
        "core_driver": driver
    }))

if __name__ == "__main__": main()

import os, json, duckdb

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    
    # 优先使用传入参数，否则从数据库获取
    c_roa = params.get("current_roa")
    p_roa = params.get("previous_roa")
    c_ocf = params.get("current_ocf")
    c_debt = params.get("current_debt_ratio")
    p_debt = params.get("previous_debt_ratio")
    c_margin = params.get("current_margin")
    p_margin = params.get("previous_margin")
    
    # 如果缺少参数，从数据库获取
    ticker = params.get("ticker")
    target_date = params.get("target_date")
    
    if ticker and any(v is None for v in [c_roa, p_roa, c_debt, p_debt, c_margin, p_margin]):
        db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
        
        # 获取最近两期财务数据
        query = """
            SELECT report_date, net_profit, total_assets, total_liabilities, total_revenue, free_cash_flow
            FROM financial_statements 
            WHERE ticker = ? AND announce_date <= ?
            ORDER BY report_date DESC LIMIT 2
        """
        df = db.execute(query, (ticker, target_date)).df()
        db.close()
        
        if len(df) >= 2:
            current = df.iloc[0]
            previous = df.iloc[1]
            
            if c_roa is None:
                c_roa = current['net_profit'] / current['total_assets'] if current['total_assets'] > 0 else 0
            if p_roa is None:
                p_roa = previous['net_profit'] / previous['total_assets'] if previous['total_assets'] > 0 else 0
            if c_ocf is None:
                c_ocf = current.get('free_cash_flow', current.get('net_profit', 0))
            if c_debt is None:
                c_debt = current['total_liabilities'] / current['total_assets'] if current['total_assets'] > 0 else 0
            if p_debt is None:
                p_debt = previous['total_liabilities'] / previous['total_assets'] if previous['total_assets'] > 0 else 0
            if c_margin is None:
                c_margin = current['net_profit'] / current['total_revenue'] if current['total_revenue'] > 0 else 0
            if p_margin is None:
                p_margin = previous['net_profit'] / previous['total_revenue'] if previous['total_revenue'] > 0 else 0
    
    # 使用默认值
    c_roa = c_roa or 0
    p_roa = p_roa or 0
    c_ocf = c_ocf or 0
    c_debt = c_debt or 0
    p_debt = p_debt or 0
    c_margin = c_margin or 0
    p_margin = p_margin or 0
    
    score = 0
    details = []

    if c_roa > 0: 
        score += 1; details.append("ROA为正 (+1)")
    if c_ocf > 0: 
        score += 1; details.append("现金流为正 (+1)")
    if c_roa > p_roa: 
        score += 1; details.append("ROA环比提升 (+1)")
    if c_ocf > c_roa: 
        score += 1; details.append("现金流大于ROA (盈利质量高) (+1)")

    if c_debt < p_debt: 
        score += 1; details.append("资产负债率下降 (去杠杆) (+1)")
        
    if c_margin > p_margin: 
        score += 1; details.append("利润率提升 (+1)")

    max_score = 6
    normalized_score = round((score / max_score) * 100, 2)
    
    health_status = "Healthy (健康)"
    if normalized_score < 40:
        health_status = "Distressed (财务困境)"
    elif normalized_score < 70:
        health_status = "Typical (表现平庸)"

    print(json.dumps({
        "raw_score": f"{score}/{max_score}",
        "normalized_score_100": normalized_score,
        "health_status": health_status,
        "scoring_details": details
    }))

if __name__ == "__main__": main()

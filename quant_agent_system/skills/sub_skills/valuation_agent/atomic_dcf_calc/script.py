import os, json, duckdb
import pandas as pd
import numpy as np

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker", "")
    target_date = params.get("target_date", "2026-03-14")
    g = params.get('perpetual_growth_rate', 0.02)
    
    if not ticker:
        raise ValueError("ERROR: ticker is required")
    
    # 标准化ticker (移除.SH/.SZ后缀)
    ticker_normalized = ticker.replace('.SH', '').replace('.SZ', '')
    
    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)

    # 🚨 红线：WHERE announce_date <= ? 防止前视偏差
    fcf_query = """
        SELECT report_date, free_cash_flow, total_equity FROM financial_statements 
        WHERE ticker = ? AND announce_date <= ? ORDER BY report_date DESC LIMIT 4
    """
    df_fcf = db.execute(fcf_query, (ticker_normalized, target_date)).df()
    
    # 获取当前股价
    price_query = "SELECT close_qfq FROM market_daily_qfq WHERE ticker = ? AND trade_date <= ? ORDER BY trade_date DESC LIMIT 1"
    price_result = db.execute(price_query, (ticker_normalized, target_date)).fetchone()
    current_price = float(price_result[0]) if price_result else 0
    
    # 数据不足时使用估算值
    if len(df_fcf) < 4:
        # 使用估算的FCF (基于净利润)
        net_profit_query = """
            SELECT net_profit FROM financial_statements 
            WHERE ticker = ? AND announce_date <= ? ORDER BY report_date DESC LIMIT 1
        """
        np_result = db.execute(net_profit_query, (ticker_normalized, target_date)).fetchone()
        if np_result:
            base_fcf = float(np_result[0]) * 0.8  # 假设FCF是净利润的80%
        else:
            base_fcf = 500000  # 默认估算
        wacc = 0.085
        projected_fcf = [base_fcf * (1 + 0.05)**i for i in range(1, 6)]
    else:
        wacc = 0.03 + 1.1 * (0.08 - 0.03) 
        base_fcf = df_fcf['free_cash_flow'].mean() * 4
        projected_fcf = [base_fcf * (1 + 0.05)**i for i in range(1, 6)]
    
    # 折现与终值
    pv_fcf = sum([fcf / (1 + wacc)**i for i, fcf in enumerate(projected_fcf, 1)])
    terminal_value = (projected_fcf[-1] * (1 + g)) / (wacc - g)
    pv_tv = terminal_value / (1 + wacc)**5
    
    enterprise_value = pv_fcf + pv_tv

    # 获取股本 (基于总权益和合理PB估算,或使用默认值)
    equity_query = "SELECT total_equity FROM financial_statements WHERE ticker = ? AND announce_date <= ? ORDER BY report_date DESC LIMIT 1"
    eq_result = db.execute(equity_query, (ticker_normalized, target_date)).fetchone()
    
    if eq_result and current_price > 0:
        total_equity = float(eq_result[0])
        if total_equity > 0:
            # total_equity 单位: 元, current_price 单位: 元/股
            # 假设合理PB=2, 则每股净资产 = current_price / 2
            # total_shares = total_equity / (current_price / 2) = total_equity * 2 / current_price
            # 结果单位为"股"
            total_shares = total_equity * 2 / current_price
        else:
            total_shares = 100000000  # 默认 1 亿股
    else:
        total_shares = 100000000  # 默认 1 亿股
        
    per_share_value = enterprise_value / total_shares
    
    print(json.dumps({
        "ticker": ticker, "target_date": target_date,
        "wacc": round(wacc, 4), 
        "enterprise_value": round(float(enterprise_value), 2),
        "per_share_value": round(per_share_value, 2),
        "current_price": round(current_price, 2),
        "total_shares": round(total_shares, 2),
        "perpetual_growth_rate": g,
        "projected_fcf_5y": [round(f, 2) for f in projected_fcf],
        "data_fallback": len(df_fcf) < 4,
        "model": "DCF"
    }))

if __name__ == "__main__": main()

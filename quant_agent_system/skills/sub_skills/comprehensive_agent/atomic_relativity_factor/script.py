import os, json, duckdb
import pandas as pd
import numpy as np

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params['ticker']
    industry = params['industry_name']
    target_date = params['target_date']

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    
    q_stock = "SELECT trade_date, close_qfq as s_close FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 60"
    df_stock = db.execute(q_stock, (ticker, target_date)).df().set_index('trade_date')
    
    q_ind = "SELECT trade_date, index_value as i_close FROM industry_daily WHERE industry=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 60"
    df_ind = db.execute(q_ind, (industry, target_date)).df().set_index('trade_date')
    
    df = df_stock.join(df_ind, how='inner').sort_index()
    if len(df) < 20: raise ValueError("DATA_MISSING: 个股或行业历史数据不足")

    stock_return = (df['s_close'].iloc[-1] / df['s_close'].iloc[0]) - 1
    ind_return = (df['i_close'].iloc[-1] / df['i_close'].iloc[0]) - 1
    
    relative_alpha = stock_return - ind_return
    
    s_pct = df['s_close'].pct_change().dropna().astype(float).values
    i_pct = df['i_close'].pct_change().dropna().astype(float).values
    beta = np.cov(s_pct, i_pct)[0,1] / np.var(i_pct) if np.var(i_pct) != 0 else 1.0

    print(json.dumps({
        "stock_return_60d_pct": round(stock_return * 100, 2),
        "industry_return_60d_pct": round(ind_return * 100, 2),
        "relative_alpha_pct": round(relative_alpha * 100, 2),
        "beta_to_industry": round(beta, 2),
        "relativity_state": "正向扭曲 (跑赢行业)" if relative_alpha > 0 else "负向扭曲 (跑输行业)"
    }))

if __name__ == "__main__": main()

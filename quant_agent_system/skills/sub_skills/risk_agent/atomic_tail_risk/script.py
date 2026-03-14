import os, json, duckdb
import numpy as np

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
        "data/db/quant_data.duckdb"
    )
    db = duckdb.connect(db_path, read_only=True)
    query = "SELECT close_qfq FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 250"
    df = db.execute(query, (ticker, target_date)).df()
    db.close()
    
    if len(df) < 200:
        raise ValueError("DATA_MISSING: 数据不足以进行尾部风险模拟")
    
    returns = df['close_qfq'].iloc[::-1].pct_change().dropna().values
    
    var_95 = np.percentile(returns, 5)
    
    tail_losses = returns[returns <= var_95]
    cvar_95 = tail_losses.mean() if len(tail_losses) > 0 else var_95

    print(json.dumps({
        "daily_VaR_95_pct": round(var_95 * 100, 2),
        "daily_CVaR_95_pct": round(cvar_95 * 100, 2),
        "tail_risk_warning": "极端尾部风险较高" if cvar_95 < -0.07 else "尾部风险可控"
    }))

if __name__ == "__main__": main()

import os, json, duckdb
import numpy as np
import pandas as pd

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
        "data/db/quant_data.duckdb"
    )
    db = duckdb.connect(db_path, read_only=True)
    query = "SELECT trade_date, close_qfq FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 250"
    df = db.execute(query, (ticker, target_date)).df()
    db.close()
    
    if len(df) < 100:
        raise ValueError("DATA_MISSING: 行情数据不足以计算长期风险指标")
    
    df = df.iloc[::-1].reset_index(drop=True)
    prices = df['close_qfq']
    returns = prices.pct_change().dropna()
    
    annual_volatility = returns.std() * np.sqrt(252)
    
    cumulative_max = prices.cummax()
    drawdown = (prices - cumulative_max) / cumulative_max
    max_drawdown = drawdown.min()

    print(json.dumps({
        "annual_volatility_pct": round(annual_volatility * 100, 2),
        "max_drawdown_pct": round(max_drawdown * 100, 2),
        "current_drawdown_pct": round(drawdown.iloc[-1] * 100, 2),
        "risk_profile": "High Volatility" if annual_volatility > 0.4 else "Stable"
    }))

if __name__ == "__main__": main()

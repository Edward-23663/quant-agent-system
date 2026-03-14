import os, json, duckdb
import numpy as np

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params['ticker']
    target_date = params['target_date']

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    query = "SELECT close_qfq FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 100"
    df = db.execute(query, (ticker, target_date)).df()
    if len(df) < 50: raise ValueError("DATA_MISSING: 数据不足无法构建波函数")
    
    df = df.iloc[::-1].reset_index(drop=True)
    returns = df['close_qfq'].pct_change().dropna()
    
    positive_energy = np.sum(returns[returns > 0] ** 2)
    negative_energy = np.sum(returns[returns < 0] ** 2)
    total_energy = positive_energy + negative_energy
    
    if total_energy == 0:
        prob_up, prob_down = 0.5, 0.5
    else:
        prob_up = positive_energy / total_energy
        prob_down = negative_energy / total_energy

    print(json.dumps({
        "quantum_state_up_prob": round(float(prob_up), 4),
        "quantum_state_down_prob": round(float(prob_down), 4),
        "dominant_state": "UP (多头叠加态)" if prob_up > 0.55 else ("DOWN (空头叠加态)" if prob_down > 0.55 else "ENTANGLED (混沌纠缠态)")
    }))

if __name__ == "__main__": main()

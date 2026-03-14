import os, json, duckdb
import numpy as np

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker, target_date = params['ticker'], params['target_date']

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    query = "SELECT close_qfq FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 500"
    df = db.execute(query, (ticker, target_date)).df()
    
    df = df.iloc[::-1].reset_index(drop=True)
    returns = np.log(1 + df['close_qfq'].pct_change().dropna())
    
    mu = returns.mean()
    sigma = returns.std()
    current_price = df['close_qfq'].iloc[-1]
    
    simulations = 1000
    days = 252
    
    simulated_paths = np.zeros((days, simulations))
    simulated_paths[0] = current_price
    for t in range(1, days):
        random_shocks = np.random.normal(0, 1, simulations)
        simulated_paths[t] = simulated_paths[t-1] * np.exp((mu - 0.5 * sigma**2) + sigma * random_shocks)
    
    final_prices = simulated_paths[-1]
    
    print(json.dumps({
        "current_price": float(current_price),
        "mc_p05": float(np.percentile(final_prices, 5)),
        "mc_p50": float(np.percentile(final_prices, 50)),
        "mc_p95": float(np.percentile(final_prices, 95))
    }))

if __name__ == "__main__": main()

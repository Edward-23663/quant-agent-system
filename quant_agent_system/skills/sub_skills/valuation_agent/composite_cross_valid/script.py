import os, json
import numpy as np

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    dcf_val = params['dcf_value']
    price = params['current_price']
    pe_pct = params['pe_percentile']
    mc_med = params['mc_median']

    dcf_premium = (dcf_val - price) / price
    mc_premium = (mc_med - price) / price
    
    conflict_flag = False
    conflict_reason = ""

    if dcf_premium > 0.3 and pe_pct > 80:
        conflict_flag = True
        conflict_reason = "严重冲突：DCF显示极度低估(>30%)，但PE处于历史极度高估区间(>80分位)。可能是近期盈利暴跌导致PE失真，或DCF参数过于乐观。"
    
    model_values = [dcf_val, mc_med]
    cv = np.std(model_values) / np.mean(model_values)

    print(json.dumps({
        "divergence_cv": round(cv, 3),
        "has_logic_conflict": conflict_flag,
        "conflict_analysis": conflict_reason,
        "reliability_score": 100 - (cv * 100) if not conflict_flag else 30
    }))

if __name__ == "__main__": main()

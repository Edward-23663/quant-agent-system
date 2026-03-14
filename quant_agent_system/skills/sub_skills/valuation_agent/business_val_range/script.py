import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    dcf_val = params['dcf_value']
    mc_p05 = params['mc_p05']
    mc_p95 = params['mc_p95']
    price = params['current_price']
    score = params.get('reliability_score', 100)

    if score < 50:
        dcf_weight = 0.3
        mc_weight = 0.7
    else:
        dcf_weight = 0.6
        mc_weight = 0.4

    lower_bound = (dcf_val * 0.8 * dcf_weight) + (mc_p05 * mc_weight)
    upper_bound = (dcf_val * 1.2 * dcf_weight) + (mc_p95 * mc_weight)

    margin_of_safety = (lower_bound - price) / lower_bound if price < lower_bound else 0

    if price < lower_bound:
        rating = "STRONG BUY (强力买入)"
    elif price > upper_bound:
        rating = "SELL (卖出)"
    else:
        rating = "HOLD (持有)"

    print(json.dumps({
        "fair_value_lower": round(lower_bound, 2),
        "fair_value_upper": round(upper_bound, 2),
        "current_price": price,
        "margin_of_safety_pct": round(margin_of_safety * 100, 2),
        "final_rating": rating,
        "business_advice": f"当前价格位于合理区间{'下方' if rating=='STRONG BUY' else '上方'}。计算得出安全边际为 {round(margin_of_safety * 100, 2)}%。"
    }))

if __name__ == "__main__": main()

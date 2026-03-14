import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    risk_score = params.get("composite_risk_score_100", 50.0)
    volatility = params.get("annual_volatility_pct", 20.0)
    price = params.get("current_price", 10.0)
    
    if risk_score > 85:
        max_position = 0.0
        pos_advice = "风险极度不可控，建议立即清仓或禁止买入 (0% 仓位)。"
    elif risk_score > 65:
        max_position = 5.0
        pos_advice = f"高危品种，严格限制单票敞口，最大持仓不应超过总资金的 {max_position}%。"
    elif risk_score > 40:
        max_position = 10.0
        pos_advice = f"风险中性，建议标准配置，最大持仓 {max_position}%。"
    else:
        max_position = 20.0
        pos_advice = f"走势稳健，可作为底仓核心资产，最大持仓可达 {max_position}%。"
    
    monthly_vol = volatility / 3.46
    stop_loss_pct = monthly_vol * 1.5
    stop_loss_price = price * (1 - (stop_loss_pct / 100))

    print(json.dumps({
        "suggested_max_position_pct": max_position,
        "position_sizing_advice": pos_advice,
        "suggested_stop_loss_price": round(stop_loss_price, 2),
        "stop_loss_logic": f"基于标的近期波动率测算，建议将硬性止损位设在现价的 -{round(stop_loss_pct, 1)}% 处。"
    }))

if __name__ == "__main__": main()

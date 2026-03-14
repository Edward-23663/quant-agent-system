import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    vol = params.get("annual_volatility_pct", 20.0)
    mdd = abs(params.get("max_drawdown_pct", -20.0))
    cvar = abs(params.get("daily_CVaR_95_pct", -3.0))
    dry_up = params.get("is_liquidity_drying_up", False)
    
    score_vol = min(100, vol * 1.5)
    score_mdd = min(100, mdd * 1.5)
    score_cvar = min(100, cvar * 10)
    
    risk_score = (score_vol * 0.2) + (score_mdd * 0.4) + (score_cvar * 0.4)
    
    if dry_up:
        risk_score = min(100, risk_score + 20)
        
    level = "LOW (低风险)"
    if risk_score > 80:
        level = "EXTREME (极度高危)"
    elif risk_score > 60:
        level = "HIGH (高风险)"
    elif risk_score > 40:
        level = "MEDIUM (中等风险)"

    print(json.dumps({
        "composite_risk_score_100": round(risk_score, 1),
        "overall_risk_level": level,
        "primary_risk_source": "最大回撤过大" if score_mdd > score_cvar else "单日暴跌尾部风险"
    }))

if __name__ == "__main__": main()

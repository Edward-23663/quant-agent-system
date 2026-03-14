import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    score = params.get("normalized_score", 50)
    debt_pct = params.get("debt_to_asset_pct", 50)
    driver = params.get("dupont_driver", "未知")
    growth = params.get("revenue_growth_pct", 0)
    
    risk_level = "LOW (低风险)"
    warnings = []
    
    if score < 40:
        warnings.append("财务健康度评分极低，存在潜在的流动性或盈利恶化风险。")
        risk_level = "HIGH (高风险)"
        
    if debt_pct > 75:
        warnings.append(f"资产负债率高达 {debt_pct}%，远超安全警戒线，面临严峻偿债压力。")
        risk_level = "HIGH (高风险)"
        
    if "高杠杆" in driver and growth < 0:
        warnings.append("杜邦分析显示高杠杆驱动，且营收出现负增长，这是典型的戴维斯双杀前兆。")
        risk_level = "EXTREME (极高风险 - 建议规避)"
        
    if risk_level == "LOW (低风险)" and growth > 15 and score > 80:
        risk_level = "EXCELLENT (优质白马)"

    business_advice = "基本面稳健，无需过度担忧财务风险。"
    if risk_level in ["HIGH (高风险)", "EXTREME (极高风险 - 建议规避)"]:
        business_advice = "⚠️ 触发排雷警报！建议在估值模型中大幅提高折现率 (WACC) 或直接一票否决。"

    print(json.dumps({
        "fundamental_risk_level": risk_level,
        "risk_warnings": warnings,
        "business_advice": business_advice
    }))

if __name__ == "__main__": main()

import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker", "Unknown")
    is_dragon = params.get("is_dragon", False)
    phase = params.get("rotation_phase", "未知")
    val_pct = params.get("valuation_percentile", 50)
    
    score = 50
    reasons = []

    if val_pct < 20:
        score += 20
        reasons.append(f"估值极具吸引力 (历史 {val_pct}% 分位)，安全边际高。")
    elif val_pct > 80:
        score -= 20
        reasons.append(f"估值处于历史危险高位 (历史 {val_pct}% 分位)，性价比极低。")
        
    if "触底反弹" in phase or "主升浪" in phase:
        score += 20
        reasons.append(f"行业处于【{phase}】，顺应资金做多趋势，胜率较高。")
    elif "阴跌寻底" in phase:
        score -= 20
        reasons.append(f"行业处于【{phase}】，逆势接飞刀风险极大，建议等待右侧信号。")
        
    if is_dragon:
        score += 10
        reasons.append("标的为行业绝对龙头，具备马太效应与抗风险溢价。")
    else:
        score -= 5
        reasons.append("标的非行业龙头，在行业下行期可能面临更大的业绩挤压风险。")

    allocation = "标配 (Neutral)"
    if score >= 80:
        allocation = "强烈超配 (Strong Overweight)"
    elif score >= 65:
        allocation = "超配 (Overweight)"
    elif score <= 35:
        allocation = "低配/规避 (Underweight)"

    print(json.dumps({
        "cost_effectiveness_score": score,
        "allocation_advice": allocation,
        "key_reasons": reasons,
        "business_conclusion": f"综合评估得分 {score}分。建议策略：{allocation}。"
    }))

if __name__ == "__main__": main()

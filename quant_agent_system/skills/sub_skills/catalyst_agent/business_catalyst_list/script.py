import os
import json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    count = params.get("valid_catalysts_count", 0)
    top_score = params.get("top_catalyst_score", 0)
    logic = params.get("adjustment_logic", "")
    
    base_prob = top_score * 8 
    density_bonus = min(20, count * 5)
    
    explosion_prob = min(99, base_prob + density_bonus)
    
    readiness = "COLD (冷却期)"
    if explosion_prob > 80:
        readiness = "IGNITED (已点火 - 极高爆发概率)"
    elif explosion_prob > 50:
        readiness = "WARM (酝酿期 - 值得潜伏)"
        
    action_plan = "当前缺乏明确的股价上行动力，建议作为观察仓或采用网格交易。"
    if readiness == "IGNITED (已点火 - 极高爆发概率)":
        action_plan = "🚀 核心催化剂已落地或即将兑现，爆发概率极高！建议立即提升仓位，享受主升浪溢价。"
    elif readiness == "WARM (酝酿期 - 值得潜伏)":
        action_plan = "催化剂正在密集发酵，建议在左侧逢低潜伏，等待市场形成共识。"

    print(json.dumps({
        "explosion_probability_pct": float(explosion_prob),
        "catalyst_readiness_state": readiness,
        "strategic_action_plan": action_plan,
        "impact_on_valuation": logic
    }))

if __name__ == "__main__":
    main()

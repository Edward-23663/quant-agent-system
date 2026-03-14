import os
import json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    top_score = params.get("top_catalyst_score", 0)
    events = params.get("scored_events", [])
    
    adj_g = 0.0
    adj_wacc = 0.0
    adj_pe = 0.0

    logic_explanation = "暂无重大催化剂，维持基准估值模型参数。"

    if top_score >= 8:
        adj_g = 1.5
        adj_pe = 5.0
        adj_wacc = -0.5
        logic_explanation = "【重大级别催化剂】（如扭亏、翻倍、百亿订单）。不仅大幅提升短期业绩预期，且显著改善长期逻辑。建议在 DCF 模型中上调永续增长率 1.5%，并给予 5 倍的 PE 估值溢价。"
        
    elif top_score >= 5:
        adj_g = 0.5
        adj_pe = 2.0
        logic_explanation = "【中等级别催化剂】（如新品发布、普通中标）。对短期业绩有提振作用，建议目标 PE 上调 2 倍，DCF 增长率微调 0.5%。"
        
    elif top_score >= 3:
        adj_wacc = -0.2
        logic_explanation = "【情绪级别催化剂】（如增持、回购）。主要改善市场微观流动性与情绪，对基本面影响有限，建议微调 WACC -0.2% 以反映风险偏好的修复。"

    print(json.dumps({
        "valuation_adjustments": {
            "suggested_g_adj_pct": adj_g,
            "suggested_wacc_adj_pct": adj_wacc,
            "suggested_pe_multiple_adj": adj_pe
        },
        "adjustment_logic": logic_explanation
    }))

if __name__ == "__main__":
    main()

import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    mom_20 = params.get("momentum_20d_pct", 0)
    mom_60 = params.get("momentum_60d_pct", 0)
    
    phase = "未知"
    logic = ""

    if mom_60 > 0 and mom_20 > 0:
        if mom_20 > mom_60:
            phase = "主升浪 (Strong Bull)"
            logic = "长短动量皆为正，且短期加速上涨，资金处于极度亢奋期，警惕过热回撤。"
        else:
            phase = "高位震荡 (Top Consolidation)"
            logic = "长期趋势向上，但短期动能减弱，可能处于派发期或蓄势期。"
            
    elif mom_60 > 0 and mom_20 < 0:
        phase = "短期回调 (Short-term Correction)"
        logic = "长期趋势依然为正，但短期遭遇获利盘兑现，可能是逢低介入的右侧买点。"
        
    elif mom_60 < 0 and mom_20 < 0:
        phase = "阴跌寻底 (Downtrend)"
        logic = "长短期皆处于空头排列，资金持续流出，左侧风险极大，建议观望。"
        
    elif mom_60 < 0 and mom_20 > 0:
        phase = "触底反弹 (Rebound / Early Bull)"
        logic = "长期趋势为负，但短期动量率先翻红，资金开始试探性建仓，可能是反转初期。"

    print(json.dumps({
        "rotation_phase": phase,
        "cycle_logic": logic,
        "trend_score": round((mom_20 * 0.6) + (mom_60 * 0.4), 2)
    }))

if __name__ == "__main__": main()

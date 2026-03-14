import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    polarity = params.get("average_polarity", 0.0)
    heat = params.get("heat_index_100", 0.0)
    divergence = params.get("has_divergence", False)
    
    risk_level = "SAFE (安全)"
    action_advice = "暂无明显舆情风险，可按既定策略持有或建仓。"
    
    if polarity < -0.6 and heat > 70:
        risk_level = "BLACK_SWAN (黑天鹅爆发)"
        action_advice = "🚨 极度危险！全网负面舆情沸腾，存在重大暴雷可能（如财务造假、实控人被抓）。建议立即清仓规避！"
    elif polarity < -0.3 and heat > 50:
        risk_level = "WARNING (风险积聚)"
        action_advice = "负面舆情开始发酵，建议暂缓买入，观察事态发展。"
    elif polarity > 0.6 and heat > 80 and divergence:
        risk_level = "BULL_TRAP (多头陷阱)"
        action_advice = "⚠️ 警惕！舆情极度狂热但股价出现滞涨背离，极大概率是主力派发筹码的多头陷阱，建议逢高减仓。"
    elif polarity > 0.5 and heat > 60 and not divergence:
        risk_level = "CATALYST (正向催化)"
        action_advice = "✅ 舆情正向发酵且量价配合良好，有望迎来主升浪行情。"

    print(json.dumps({
        "sentiment_risk_level": risk_level,
        "composite_score": round((polarity * 50) + 50, 1),
        "action_advice": action_advice
    }))

if __name__ == "__main__": main()

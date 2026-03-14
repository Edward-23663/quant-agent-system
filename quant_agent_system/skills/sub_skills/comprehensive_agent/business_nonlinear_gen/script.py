import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    state = params.get("system_state", "Noise")
    entropy = params.get("entropy_score", 1.0)
    conf = params.get("bullish_confidence", 50.0)
    
    strategy = "无明确策略，建议空仓观望。"
    insight = ""

    if "正向奇异吸引子" in state:
        strategy = "右侧追高/趋势跟踪 (Trend Following)"
        insight = f"系统已进入自我强化的正反馈循环（多头置信度 {conf}%）。传统估值可能失效，动量主导市场，建议不要轻易猜顶，持有至 Hurst 指数跌破 0.5。"
        
    elif "负向奇异吸引子" in state:
        strategy = "融券做空/坚决止损 (Cut Losses)"
        insight = "系统处于负反馈崩盘螺旋中，任何抢反弹的行为都属于接飞刀。必须等待熵值重新升高（分叉点出现）才能考虑抄底。"
        
    elif "极限环" in state:
        strategy = "网格交易/高抛低吸 (Mean Reversion)"
        insight = "系统处于高度规律的均值回归状态。越跌越买，越涨越卖，严格执行左侧逆势策略。"
        
    elif "分叉点" in state:
        strategy = "跨式期权/突破跟随 (Straddle / Breakout)"
        insight = f"系统熵值极高 ({entropy})，处于混沌的临界点。即将发生剧烈的方向性选择。建议使用期权做多波动率，或等待放量突破后第一时间跟随。"

    print(json.dumps({
        "nonlinear_strategy": strategy,
        "deep_insight": insight,
        "warning": "本结论基于非线性动力学模型，适用于应对极端市场行情与肥尾效应 (Fat Tails)。"
    }))

if __name__ == "__main__": main()

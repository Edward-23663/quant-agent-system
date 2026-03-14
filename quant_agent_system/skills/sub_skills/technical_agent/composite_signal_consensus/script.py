import os
import json


def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ma = params.get("ma_trend", "")
    macd = params.get("macd_status", "")
    rsi = params.get("rsi_status", "")
    kdj = params.get("kdj_cross", "")
    vol = params.get("vol_status", "")
    obv = params.get("obv_trend", "")

    bullish_score = 0
    bearish_score = 0
    divergence_warnings = []

    if "Bullish" in ma or "多头" in ma:
        bullish_score += 2
    if "Bearish" in ma or "空头" in ma:
        bearish_score += 2
    if "Golden" in macd or "金叉" in macd:
        bullish_score += 2
    if "Death" in macd or "死叉" in macd:
        bearish_score += 2

    if "Oversold" in rsi or "超卖" in rsi:
        bullish_score += 1
    if "Overbought" in rsi or "超买" in rsi:
        bearish_score += 1
    if "Golden" in kdj or "金叉" in kdj:
        bullish_score += 1
    if "Death" in kdj or "死叉" in kdj:
        bearish_score += 1

    if "Accumulation" in obv:
        bullish_score += 1
    if "Distribution" in obv:
        bearish_score += 1

    if ("Bullish" in ma or "多头" in ma) and "Distribution" in obv:
        divergence_warnings.append("【顶背离警告】：价格维持多头趋势，但OBV显示资金正在暗中撤退 (量价背离)。")
    if ("Bearish" in ma or "空头" in ma) and "Accumulation" in obv:
        divergence_warnings.append("【底背离信号】：价格处于下跌趋势，但OBV显示资金正在低位暗中吸筹。")
    if "Bullish" in ma and ("Overbought" in rsi or "超买" in rsi):
        divergence_warnings.append("【回调预警】：右侧趋势极强，但RSI显示严重超买，短期随时可能面临技术性回调。")

    consensus = "震荡无方向 (Neutral)"
    if bullish_score >= 5 and bearish_score <= 1:
        consensus = "强烈看多 (Strong Buy - 指标共振)"
    elif bearish_score >= 5 and bullish_score <= 1:
        consensus = "强烈看空 (Strong Sell - 指标共振)"
    elif bullish_score > bearish_score:
        consensus = "偏多 (Bullish Bias)"
    elif bearish_score > bullish_score:
        consensus = "偏空 (Bearish Bias)"

    print(json.dumps({
        "bullish_signals_count": bullish_score,
        "bearish_signals_count": bearish_score,
        "technical_consensus": consensus,
        "divergence_warnings": divergence_warnings
    }))


if __name__ == "__main__":
    main()
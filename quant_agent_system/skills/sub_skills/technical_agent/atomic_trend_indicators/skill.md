# 技能名称: atomic_trend_indicators
## 功能描述
计算标的的趋势指标，包括移动平均线 (MA5/MA20/MA60) 的多空排列、MACD (平滑异同移动平均线) 的金叉死叉状态，以及 BOLL (布林带) 的轨道位置。
## 入参格式 (JSON)
- ticker (str): 股票代码
- target_date (str): 观察日期
## 出参格式 (JSON)
- current_price: 当前价格
- ma_system: MA均线系统 (ma5, ma20, ma60, trend)
- macd_system: MACD指标 (macd_val, signal_val, hist, status)
- boll_system: BOLL布林带 (upper, mid, lower, position)

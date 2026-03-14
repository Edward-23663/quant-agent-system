# 技能名称: composite_signal_consensus
## 功能描述
汇总趋势 (MA/MACD)、动量 (RSI/KDJ) 和量价 (OBV) 的底层信号，通过规则引擎检测指标之间是否产生"共振 (Consensus)"或"背离 (Divergence)"。
## 入参格式 (JSON)
- ma_trend (str): MA趋势状态
- macd_status (str): MACD状态
- rsi_status (str): RSI状态
- kdj_cross (str): KDJ交叉信号
- vol_status (str): 成交量状态
- obv_trend (str): OBV资金趋势
## 出参格式 (JSON)
- bullish_signals_count: 看多信号数量
- bearish_signals_count: 看空信号数量
- technical_consensus: 技术面共振结论
- divergence_warnings: 背离警告列表
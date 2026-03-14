# 技能名称: composite_fact_alignment
## 功能描述
检测基本面信号、估值信号与舆情信号之间是否存在逻辑背离（如：基本面极差但估值极度高估）。
## 入参格式 (JSON)
- fundamental_score (int): 基本面健康度评分 0-100
- valuation_rating (str): "STRONG BUY", "BUY", "HOLD", "SELL"
- sentiment_polarity (float): 舆情极性 -1.0 到 1.0

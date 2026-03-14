# 技能名称: business_risk_assess
## 功能描述
综合情感极性、讨论热度和量价背离情况，评估标的当前面临的"舆情黑天鹅"风险等级。
## 入参格式 (JSON)
- average_polarity (float): 平均极性 (-1.0 到 1.0)
- heat_index_100 (float): 热度指数 (0-100)
- has_divergence (bool): 是否存在量价舆情背离

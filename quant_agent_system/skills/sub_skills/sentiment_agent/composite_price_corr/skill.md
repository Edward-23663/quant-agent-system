# 技能名称: composite_price_corr
## 功能描述
将最近的舆情极性与近5日的真实股价涨跌幅进行关联分析，检测是否存在"利好出尽"或"错杀背离"的现象。
## 入参格式 (JSON)
- ticker (str)
- target_date (str)
- sentiment_label (str): 当前舆情标签 (POSITIVE/NEGATIVE/NEUTRAL)

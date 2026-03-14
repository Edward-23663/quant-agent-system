# 技能名称: atomic_impact_scoring

## 功能描述
对提取出的催化剂事件文本进行硬核正则匹配与词频分析，量化其对营收或利润的影响力度 (0-10分)。

## 入参格式 (JSON)
- raw_events (List[Dict]): 包含 "text" 的事件列表

# 技能名称: composite_event_val_corr

## 功能描述
将催化剂事件的量化得分，映射为估值模型的核心参数调整建议（如：DCF的永续增长率 g，或者目标 PE 倍数）。为主编排器融合估值报告提供依据。

## 入参格式 (JSON)
- top_catalyst_score (int): 最高催化剂得分
- scored_events (List[Dict]): 打分后的事件列表

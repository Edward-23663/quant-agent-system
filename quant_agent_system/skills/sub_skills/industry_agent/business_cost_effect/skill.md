# 技能名称: business_cost_effect
## 功能描述
综合行业周期、龙头地位和估值水位，评估当前买入或持有该标的的"盈亏比(性价比)"，并给出明确的资产配置建议（超配/标配/低配）。
## 入参格式 (JSON)
- ticker (str): 股票代码
- is_dragon (bool): 该票是否在行业 Top 5 龙头列表中
- rotation_phase (str): 行业轮动阶段 (如 "触底反弹")
- valuation_percentile (float): 估值历史分位数 (0-100，低代表便宜)

# 技能名称: business_val_range
## 功能描述
基于交叉验证通过的多模型数据，赋予不同权重（如基本面驱动型赋予 DCF 更高权重），计算最终的"绝对合理估值区间"，并输出当前的"安全边际(Margin of Safety)"。
## 入参格式 (JSON)
- dcf_value (float)
- mc_p05 (float)
- mc_p95 (float)
- current_price (float)
- reliability_score (float): 交叉验证给出的可靠性评分

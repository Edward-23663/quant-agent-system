# 技能名称: business_risk_value
## 功能描述
基于基本面评分、杠杆率和杜邦核心驱动力，评估该标的的长期投资基本面风险，并生成可直接用于研报的业务结论。
## 入参格式 (JSON)
- normalized_score (float): 0-100 的财务健康度评分
- debt_to_asset_pct (float): 资产负债率百分比
- dupont_driver (str): 杜邦分析结论 (如 "高杠杆驱动")
- revenue_growth_pct (float): 营收增速百分比

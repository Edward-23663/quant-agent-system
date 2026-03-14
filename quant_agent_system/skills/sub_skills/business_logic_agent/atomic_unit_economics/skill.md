# 技能名称: atomic_unit_economics
## 功能描述
提取标的近期的毛利率、销售费用率、研发费用率，拆解其单位经济模型（Unit Economics），判断这是一家靠"产品驱动"、"营销驱动"还是"规模成本驱动"的公司。
## 入参格式 (JSON)
- ticker (str): 股票代码
- target_date (str): 观察日期
## 出参格式 (JSON)
- unit_economics: 毛利率、销售费用率、研发费用率
- business_driver_hypothesis: 驱动力假说
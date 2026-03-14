# 技能名称: composite_first_principles
## 功能描述
综合单位经济模型和护城河定性证据，用第一性原理推演出公司的终极护城河分类（无形资产、转换成本、网络效应、成本优势）。
## 入参格式 (JSON)
- gross_margin_pct (float): 毛利率
- business_driver_hypothesis (str): 驱动力假说
- raw_evidence (List[str]): 检索到的定性证据
## 出参格式 (JSON)
- first_principle_moat: 护城河类型列表
- logical_deduction: 逻辑推演说明
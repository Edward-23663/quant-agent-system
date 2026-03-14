# 技能名称: atomic_bayesian_valid
## 功能描述
应用贝叶斯定理，根据新传入的利好/利空证据，动态更新标的上涨的主观概率（从先验概率更新为后验概率）。
## 入参格式 (JSON)
- prior_prob (float): 先验上涨概率 (如根据动量得出的 0.5)
- evidence_strength (float): 新证据的支持力度 (1.0=中性, >1=强力好消息, <1=坏消息)

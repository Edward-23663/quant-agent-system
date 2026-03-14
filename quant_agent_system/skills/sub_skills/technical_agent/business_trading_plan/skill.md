# 技能名称: business_trading_plan
## 功能描述
通过寻找过去半年的局部高低点和密集成交区，计算出绝对的"第一支撑位"、"第一阻力位"。结合技术共振信号，输出一份包含入场点、目标价和严格止损价的实战交易计划。
## 入参格式 (JSON)
- ticker (str)
- target_date (str)
- technical_consensus (str): 技术面共振结论
- current_price (float): 当前股价
## 出参格式 (JSON)
- key_levels: 支撑阻力位 (resistance_1, resistance_2, support_1, support_2)
- trading_plan: 交易计划 (strategy, entry_zone, target_price, stop_loss_price, reward_risk_ratio)
- executionadvice: 执行建议
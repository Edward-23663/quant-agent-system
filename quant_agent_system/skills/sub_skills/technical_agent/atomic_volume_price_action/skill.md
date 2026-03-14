# 技能名称: atomic_volume_price_action
## 功能描述
分析成交量与价格的配合关系。计算 OBV (能量潮指标) 判断资金是在潜伏吸筹还是在派发，以及成交量是否出现异动（放量突破/缩量企稳）。
## 入参格式 (JSON)
- ticker (str)
- target_date (str)
## 出参格式 (JSON)
- volume_action: 成交量状态 (current_vol, vol_ma20, status)
- OBV_indicator: OBV能量潮 (trend, logic)
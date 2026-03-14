# 技能名称: business_risk_control
## 功能描述
基于综合风险等级和波动率，生成严苛的交易风控建议，包括：最大建议持仓比例（基于风险平价理念）和动态技术止损位。
## 入参格式 (JSON)
- composite_risk_score_100 (float): 综合风险评分
- annual_volatility_pct (float): 年化波动率
- current_price (float): 当前股价

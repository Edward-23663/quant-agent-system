# 技能名称: composite_risk_matrix
## 功能描述
将波动率、最大回撤、CVaR 和流动性指标融合为一个整体的"综合风险指数 (0-100)"，分数越高代表风险越极端。
## 入参格式 (JSON)
- annual_volatility_pct (float)
- max_drawdown_pct (float)
- daily_CVaR_95_pct (float)
- is_liquidity_drying_up (bool)

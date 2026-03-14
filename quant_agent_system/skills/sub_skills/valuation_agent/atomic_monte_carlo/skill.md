# 技能名称: atomic_monte_carlo
## 功能描述
基于几何布朗运动(GBM)，利用过去 500 天的波动率和漂移率，模拟未来 252 个交易日的价格路径，输出价格分布概率。
## 业务约束
必须使用前复权 (QFQ) 价格计算收益率。
## 入参格式 (JSON)
- ticker (str), target_date (str)

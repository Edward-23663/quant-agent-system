# 技能名称: atomic_dcf_calc
## 功能描述
基于自由现金流折现模型(DCF)，计算标的资产的绝对估值。自动计算 WACC（基于 CAPM 模型）和永续增长终值(TV)。
## 业务约束
只允许使用 target_date 之前已公告的财务数据。
## 入参格式 (JSON)
- ticker (str): 股票代码，如 "600519.SH"
- target_date (str): 估值基准日，如 "2023-12-31"
- perpetual_growth_rate (float, 默认0.02): 永续增长率假设

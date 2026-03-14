# 技能名称: composite_health_scoring
## 功能描述
基于 Piotroski F-Score 模型，对企业的盈利质量、杠杆与流动性、营运效率进行综合打分 (满分9分)。

## 入参格式 (JSON)
两种方式：
1. 手动传入: current_roa, previous_roa, current_ocf, current_debt_ratio, previous_debt_ratio, current_margin, previous_margin
2. 自动获取 (推荐): 传入 ticker 和 target_date，自动从数据库获取需要的财务数据

示例:
- ticker: "600519"
- target_date: "2023-12-31"

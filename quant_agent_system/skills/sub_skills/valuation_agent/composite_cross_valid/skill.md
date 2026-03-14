# 技能名称: composite_cross_valid
## 功能描述
接收 DCF、相对估值、蒙特卡洛三个原子技能的输出结果，计算它们之间的离散度（CV），判断估值逻辑是否存在严重冲突（例如 DCF 极度低估，但 PE 处于历史 99% 分位）。
## 入参格式 (JSON)
- dcf_value (float): DCF 计算出的每股内在价值
- current_price (float): 当前股价
- pe_percentile (float): PE 历史分位数
- mc_median (float): 蒙特卡洛中位数

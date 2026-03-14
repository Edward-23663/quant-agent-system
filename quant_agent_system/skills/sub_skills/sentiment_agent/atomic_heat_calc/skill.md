# 技能名称: atomic_heat_calc
## 功能描述
根据召回新闻的数量和时间衰减权重，计算标的当前的"舆情热度指数 (0-100)"。热度突增通常预示着变盘。
## 入参格式 (JSON)
- retrieved_count (int): 检索到的相关新闻总数
- average_polarity (float): 平均情感极性

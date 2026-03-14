# 技能名称: business_nonlinear_gen
## 功能描述
基于多模型融合的系统状态（如分叉点、吸引子），生成非线性的交易策略与风险提示（如突破跟随、网格套利或空仓观望）。
## 入参格式 (JSON)
- system_state (str): 复杂系统状态
- entropy_score (float): 系统熵
- bullish_confidence (float): 多头置信度

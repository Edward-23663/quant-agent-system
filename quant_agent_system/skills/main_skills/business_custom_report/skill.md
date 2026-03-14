# 技能名称: business_custom_report
## 功能描述
根据用户指定的报告类型（如 summary/deep_dive/risk_only），对 assembled_markdown 进行裁剪或重组。
## 入参格式 (JSON)
- report_type (str): "summary" (一页纸简报), "deep_dive" (深度研报), "risk_only" (排雷报告)
- full_markdown (str): 完整组装好的 Markdown
- conflict_warnings (List[str]): 事实对齐技能产生的冲突警告

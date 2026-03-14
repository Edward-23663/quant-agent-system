# 技能名称: composite_template_filling
## 功能描述
将各个维度的独立分析段落，组装成带有免责声明的完整研报结构。
## 入参格式 (JSON)
- ticker (str): 股票代码
- company_name (str): 公司名称
- sections (Dict): 包含 'executive_summary', 'fundamental', 'valuation', 'catalyst' 等键的 Markdown 文本字典。

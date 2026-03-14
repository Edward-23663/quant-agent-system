# 技能名称: atomic_moat_extraction
## 功能描述
基于 RAG 检索本地知识库，提取管理层或深度研报中关于该公司的"核心竞争力"、"定价权(提价能力)"、"市占率"或"用户粘性"的定性描述。
## 入参格式 (JSON)
- ticker (str)
## 出参格式 (JSON)
- ticker: 股票代码
- moat_evidence_found: 是否找到护城河证据
- raw_evidence: 定性证据列表
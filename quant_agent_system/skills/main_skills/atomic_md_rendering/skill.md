# 技能名称: atomic_md_rendering
## 功能描述
使用 Jinja2 引擎将变量注入到 Markdown 模板中，生成格式统一的文本段落。
## 入参格式 (JSON)
- template_string (str): 包含 {{ var }} 的 Markdown 模板字符串
- context (Dict): 需要注入的变量字典

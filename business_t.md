business_trading
我们将在主编排器的专属技能库中，新增一个 **`business_trading_strategy`** 技能。它会提取各维度智能体的核心结论，通过纯 Python 规则引擎，输出**短、中、长三个时间维度的买卖决策**，并最终拼接到总报告的末尾。


---

### 🗂️ 一、 新增技能目录与文件

请在 `skills/main_skills/` 目录下新建 `business_trading_strategy` 文件夹，并创建以下三个文件：

#### 1. `config.json`

主智能体不直接查 DuckDB，依赖分智能体传递的数据。

```json
{ "required_data": [] }
```

#### 2. `skill.md` (写给主智能体 LLM 看)

```markdown
# 技能名称: business_trading_strategy
## 功能描述
基于各分智能体（基本面、估值、舆情、行业、催化剂）的汇总信号，通过量化规则矩阵，生成短期（1个月内）、中期（1-6个月）、长期（1-3年）的明确买卖操作决策与仓位建议。
## 入参格式 (JSON)
- valuation_status (str): 估值状态 (如 "Undervalued", "Overvalued", "Fair")
- fundamental_score (int): 基本面健康度评分 (0-100)
- industry_phase (str): 行业轮动阶段 (如 "主升浪", "触底反弹", "阴跌寻底")
- catalyst_readiness (str): 催化剂状态 (如 "IGNITED", "WARM", "COLD")
- sentiment_risk (str): 舆情风险等级 (如 "SAFE", "BLACK_SWAN", "WARNING")
```

#### 3. `script.py` (纯 Python 交易规则引擎)

这个脚本将非结构化的文本标签转化为确定性的交易指令，并生成精美的 Markdown 段落。

```python
import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    
    # 获取参数，设置默认值以防 LLM 遗漏
    val_status = str(params.get("valuation_status", "Fair")).upper()
    fund_score = int(params.get("fundamental_score", 50))
    ind_phase = str(params.get("industry_phase", "未知"))
    catalyst = str(params.get("catalyst_readiness", "COLD")).upper()
    sentiment = str(params.get("sentiment_risk", "SAFE")).upper()

    # --- 1. 短期策略 (1个月内)：情绪、催化剂与动量主导 ---
    st_action = "观望 (WAIT & SEE)"
    st_logic = "短期缺乏明显催化剂，资金情绪平稳，建议耐心等待右侧突破信号。"
    
    if "BLACK_SWAN" in sentiment or "WARNING" in sentiment:
        st_action = "坚决卖出/回避 (STRONG SELL)"
        st_logic = "短期遭遇严重负面舆情或黑天鹅，情绪极度恐慌，切勿盲目接飞刀，立刻规避！"
    elif "IGNITED" in catalyst:
        st_action = "积极做多/追涨 (STRONG BUY)"
        st_logic = "核心催化剂已点火，短期爆发概率极高，顺应资金动量，建议立刻右侧建仓跟进。"
    elif "主升浪" in ind_phase:
        st_action = "持有/逢低买入 (HOLD/BUY)"
        st_logic = "行业处于主升浪，短期动能充沛，沿均线持有，缩量回调即是买点。"

    # --- 2. 中期策略 (1-6个月)：行业周期与相对估值主导 ---
    mt_action = "标配 (NEUTRAL)"
    mt_logic = "行业周期特征不明显，估值处于合理区间，建议维持标准配置，高抛低吸。"
    
    if "阴跌寻底" in ind_phase:
        mt_action = "低配/减仓 (UNDERWEIGHT)"
        mt_logic = "行业处于探底周期，中期趋势向下，建议降低仓位，防范阴跌耗损时间成本。"
    elif ("触底反弹" in ind_phase or "主升浪" in ind_phase) and ("UNDERVALUED" in val_status or "FAIR" in val_status):
        mt_action = "超配 (OVERWEIGHT)"
        mt_logic = "行业迎来景气度拐点，且估值具备吸引力，中期存在戴维斯双击可能，建议超配。"
    elif "OVERVALUED" in val_status:
        mt_action = "逢高减持 (REDUCE)"
        mt_logic = "中期估值已透支未来业绩预期，性价比降低，建议随着行情冲高逐步兑现利润。"

    # --- 3. 长期策略 (1-3年)：基本面与绝对安全边际主导 ---
    lt_action = "持有观察 (HOLD)"
    lt_logic = "基本面尚可，但缺乏绝对的安全边际，作为长期底仓需密切跟踪财报表现。"
    
    if fund_score < 40:
        lt_action = "长期剔除 (AVOID)"
        lt_logic = f"基本面健康度极差 (评分仅 {fund_score})，存在长期价值毁灭或退市风险，坚决剔除出核心股票池。"
    elif fund_score >= 80 and "UNDERVALUED" in val_status:
        lt_action = "核心重仓 (CORE BUY)"
        lt_logic = f"优质白马股 (基本面评分 {fund_score})，且当前处于被错杀的绝对低估区间，是长期资金绝佳的击球区，建议越跌越买，锁仓做时间的朋友。"
    elif fund_score >= 70 and "OVERVALUED" in val_status:
        lt_action = "持有但不加仓 (HOLD)"
        lt_logic = "公司质地优秀，但当前价格已无安全边际。建议底仓锁仓享受成长，但切勿在此位置追高加仓。"

    # --- 组装 Markdown 模块 ---
    strategy_md = f"""
## 五、 🎯 综合交易策略与操作建议 (Actionable Advice)

基于多维度量化模型的信号共振，系统生成以下短、中、长期操作决策：

### ⚡ 短期 (0-1个月)：事件与情绪博弈
* **操作指令**：**{st_action}**
* **逻辑支撑**：{st_logic}

### 🌊 中期 (1-6个月)：行业周期与估值修复
* **操作指令**：**{mt_action}**
* **逻辑支撑**：{mt_logic}

### ⛰️ 长期 (1-3年)：基本面与安全边际
* **操作指令**：**{lt_action}**
* **逻辑支撑**：{lt_logic}

> **🤖 智能体风控提示**：以上策略由系统基于量化规则矩阵自动生成。交易执行时请严格结合个人资金性质，并遵守 `RiskAgent` 提供的最大回撤止损线。
"""

    print(json.dumps({
        "trading_strategy_markdown": strategy_md,
        "short_term_action": st_action,
        "medium_term_action": mt_action,
        "long_term_action": lt_action
    }))

if __name__ == "__main__": main()
```

---

### 🛠️ 二、 修改研报组装模板 (关键一步)

为了让这段生成的“买卖建议”**自动添加到总报告的最末尾**，我们需要修改主智能体的装配车间：`skills/main_skills/composite_template_filling/script.py`。

打开该文件，找到组装 `report` 字符串的地方，修改为如下代码：

```python
# 修改 skills/main_skills/composite_template_filling/script.py

import os, json
from datetime import datetime

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker", "Unknown")
    name = params.get("company_name", "Unknown")
    sections = params.get("sections", {})
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 组装券商级研报骨架
    report = f"""# 深度量化投资分析报告：{name} ({ticker})
**报告生成日期**：{today}  
**由金融量化分析智能体系统 (Agentic Workflow) 自动生成**

---

## 一、 执行摘要 (Executive Summary)
{sections.get('executive_summary', '暂无摘要数据。')}

## 二、 基本面与财务健康度剖析
{sections.get('fundamental', '暂无基本面分析。')}

## 三、 多模型绝对与相对估值测算
{sections.get('valuation', '暂无估值数据。')}

## 四、 舆情追踪与事件催化剂
{sections.get('catalyst', '暂无催化剂数据。')}

{sections.get('trading_strategy', '')}  <--- 【新增这一行：将操作建议拼接到免责声明之前】

---
### ⚠️ 免责声明 (Disclaimer)
*本报告由本地私有化部署的 AI 智能体基于历史公开数据计算生成。系统已强制隔离前视偏差，但所有估值模型均基于特定假设。本报告仅供学术研究与系统测试使用，绝对不构成任何投资建议。市场有风险，投资需谨慎。*
"""
    
    print(json.dumps({
        "assembled_markdown": report
    }))

if __name__ == "__main__": main()
```

---

### 💡 三、 架构师解析：它是如何运作的？

1. **主编排器的调度**：当所有分智能体（估值、基本面、催化剂等）执行完毕后，主编排器（LLM）会统揽全局，提取出关键标签（比如：`fundamental_score=85`, `catalyst_readiness=IGNITED`）。
2. **规则引擎接管**：主编排器调用 `business_trading_strategy` 技能。此时大模型闭嘴，纯 Python 脚本接管。脚本根据预设的“多因子共振打分卡”，硬核推导出**“短期追涨、中期超配、长期核心重仓”**的结论。
3. **末尾注入**：脚本生成的 Markdown 文本被传递给 `composite_template_filling`，完美地镶嵌在研报的第五章（免责声明的上方）。

这样一来，你的系统产出的研报就不再是模棱两可的“车轱辘话”，而是**像顶尖对冲基金经理一样，敢于给出明确的交易指令与逻辑支撑！**


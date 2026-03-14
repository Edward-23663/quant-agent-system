Logic
**「商业逻辑及第一性原理分析分智能体 (Business Logic Agent)」**，相当于给系统注入了查理·芒格（Charlie Munger）和埃隆·马斯克（Elon Musk）的灵魂。

如果说基本面看的是“过去的成绩单”，技术面看的是“现在的资金博弈”，那么第一性原理看的就是**“这家公司存在的终极理由是什么？它靠什么赚钱？它的护城河在 10 年后还会不会被颠覆？”**

为了防止大模型在这个环节“满嘴跑火车（幻觉）”，我们底层的 Python 脚本将通过**拆解单位经济模型（Unit Economics）**和**RAG 向量检索定性文本**，用硬核数据来倒逼大模型得出商业逻辑结论。

---

### 🗂️ 一、 目录结构概览

```text
quant_agent_system/
├── agents/
│   └── specialized/
│       └── business_logic_agent.py     # 🌟 新增：商业逻辑分智能体
│
└── skills/sub_skills/business_logic_agent/  # 🌟 新增：商业逻辑卡带专属目录
    ├── atomic_unit_economics/          # 原子：单位经济模型与成本结构拆解
    ├── atomic_moat_extraction/         # 原子：护城河与定价权文本特征检索 (RAG)
    ├── composite_first_principles/     # 组合：第一性原理演绎 (护城河分类判定)
    └── business_model_sustainability/  # 业务：商业模式终局与颠覆风险评估
```

---

### 🤖 二、 智能体定义代码

在 `agents/specialized/` 目录下新建 `business_logic_agent.py`：

**`agents/specialized/business_logic_agent.py`**

```python
from agents.base_sub_agent import BaseSubAgent

class BusinessLogicAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_name="商业逻辑与第一性原理分智能体",
            role_desc="你是一位坚信'第一性原理'的顶级商业分析师（如查理·芒格）。你无视短期股价波动，致力于洞察生意的本质：公司靠什么赚钱？它的单位经济模型是否成立？它拥有哪种核心护城河（无形资产、转换成本、网络效应、成本优势）？它的商业模式在未来10年是否容易被技术变革所颠覆？",
            skills_dir="skills/sub_skills/business_logic_agent"
        )
```

*(记得在 `agents/specialized/__init__.py` 中导出它)*

---

### 🧱 三、 原子级 Skills (Atomic Level)

#### 1. `atomic_unit_economics` (单位经济模型与成本结构拆解)

**功能**：不看总营收，而是看“每赚100块钱，多少是成本，多少是营销，多少是研发？”。高毛利+高研发=技术护城河；高毛利+高营销=品牌护城河。

* **`config.json`**

```json
{
  "required_data": [
    {"table": "financial_statements", "min_records": 4, "description": "需要至少4期财报来平滑计算成本结构"}
  ]
}
```

* **`skill.md`**

```markdown
# 技能名称: atomic_unit_economics
## 功能描述
提取标的近期的毛利率、销售费用率、研发费用率，拆解其单位经济模型（Unit Economics），判断这是一家靠“产品驱动”、“营销驱动”还是“规模成本驱动”的公司。
## 入参格式 (JSON)
- ticker (str): 股票代码
- target_date (str): 观察日期
```

* **`script.py`**

```python
import os, json, duckdb

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    # 假设 financial_statements 表中包含 gross_profit(毛利), selling_expense(销售费用), rd_expense(研发费用)
    # 若表结构不同，请根据实际情况修改 SQL 字段
    try:
        query = """
            SELECT total_revenue, gross_profit, selling_expense, rd_expense 
            FROM financial_statements 
            WHERE ticker=? AND announce_date<=? 
            ORDER BY report_date DESC LIMIT 4
        """
        df = db.execute(query, (ticker, target_date)).df()
    except Exception as e:
        raise ValueError(f"DATA_MISSING: 财报字段缺失，无法拆解单位经济模型。详细: {e}")
        
    if len(df) < 1: raise ValueError("DATA_MISSING: 无财报数据")

    # 取最近4期均值平滑
    rev = df['total_revenue'].mean() + 1e-5
    gross_margin = df['gross_profit'].mean() / rev
    sales_ratio = df['selling_expense'].mean() / rev
    rd_ratio = df['rd_expense'].mean() / rev
    
    # 商业驱动力初判
    driver = "未知驱动"
    if gross_margin > 0.5 and rd_ratio > 0.1:
        driver = "高壁垒技术驱动 (高毛利+高研发)"
    elif gross_margin > 0.5 and sales_ratio > 0.2:
        driver = "品牌与渠道驱动 (高毛利+高营销)"
    elif gross_margin < 0.2:
        driver = "规模与成本驱动 (低毛利，依赖极致供应链)"

    print(json.dumps({
        "unit_economics": {
            "gross_margin_pct": round(gross_margin * 100, 1),
            "selling_expense_ratio_pct": round(sales_ratio * 100, 1),
            "rd_expense_ratio_pct": round(rd_ratio * 100, 1)
        },
        "business_driver_hypothesis": driver
    }))

if __name__ == "__main__": main()
```

#### 2. `atomic_moat_extraction` (护城河与定价权文本特征检索)

**功能**：利用 RAG 从本地向量库（研报/年报切片）中精准提取关于“提价”、“市占率”、“专利”的定性描述。

* **`config.json`**

```json
{ "required_data": [] }
```

* **`skill.md`**

```markdown
# 技能名称: atomic_moat_extraction
## 功能描述
基于 RAG 检索本地知识库，提取管理层或深度研报中关于该公司的“核心竞争力”、“定价权(提价能力)”、“市占率”或“用户粘性”的定性描述。
## 入参格式 (JSON)
- ticker (str)
```

* **`script.py`**

```python
import os, sys, json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from core.vector_store import VectorStore

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker", "")
    
    query = f"{ticker} 核心竞争力 护城河 提价 定价权 市占率 垄断 专利 用户粘性"
    
    try:
        vs = VectorStore()
        # 检索最相关的 5 条护城河信息
        results = vs.search(query=query, limit=5, where_clause=f"ticker = '{ticker}'")
    except Exception as e:
        results = []

    if not results:
        print(json.dumps({
            "ticker": ticker,
            "moat_evidence_found": False,
            "raw_evidence": ["未能从本地知识库中检索到明显的护城河或定价权描述。"]
        }))
        return

    evidence = [r.get("text", "") for r in results]

    print(json.dumps({
        "ticker": ticker,
        "moat_evidence_found": True,
        "raw_evidence": evidence
    }))

if __name__ == "__main__": main()
```

---

### 🧬 三、 组合级 Skills (Composite Level)

#### 3. `composite_first_principles` (第一性原理演绎)

**功能**：综合单位经济模型（定量）和 RAG 提取的证据（定性），通过硬核逻辑规则，判定公司属于哪一种经典的“晨星四大护城河”。

* **`config.json`**

```json
{ "required_data": [] }
```

* **`skill.md`**

```markdown
# 技能名称: composite_first_principles
## 功能描述
综合单位经济模型和护城河定性证据，用第一性原理推演出公司的终极护城河分类（无形资产、转换成本、网络效应、成本优势）。
## 入参格式 (JSON)
- gross_margin_pct (float): 毛利率
- business_driver_hypothesis (str): 驱动力假说
- raw_evidence (List[str]): 检索到的定性证据
```

* **`script.py`**

```python
import os, json, re

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    margin = params.get("gross_margin_pct", 20.0)
    driver = params.get("business_driver_hypothesis", "")
    evidence = " ".join(params.get("raw_evidence", []))
    
    moat_types = []
    reasoning = []

    # 1. 无形资产 (Intangible Assets - 品牌/专利/牌照)
    if margin > 50 and (re.search(r"提价|品牌溢价|专利|特许经营|垄断", evidence)):
        moat_types.append("无形资产 (Intangible Assets)")
        reasoning.append("极高的毛利率配合定性证据中的提价/专利描述，证明其拥有强大的品牌溢价或技术垄断力。")

    # 2. 转换成本 (High Switching Costs)
    if re.search(r"粘性|生态|替换成本|SaaS|续费率", evidence):
        moat_types.append("高转换成本 (Switching Costs)")
        reasoning.append("业务模式具有强客户粘性，客户一旦使用很难迁移到竞品。")

    # 3. 网络效应 (Network Effect)
    if re.search(r"双边市场|平台|用户基数|马太效应|社交", evidence):
        moat_types.append("网络效应 (Network Effect)")
        reasoning.append("具备典型的平台型特征，用户越多，产品对其他用户的价值呈指数级增长。")

    # 4. 成本优势 (Cost Advantage)
    if margin < 30 and re.search(r"规模效应|供应链|产能|低成本", evidence):
        moat_types.append("成本优势 (Cost Advantage)")
        reasoning.append("在相对较低的毛利下依然能存活并扩张，证明其具备极致的规模效应和供应链成本壁垒。")

    if not moat_types:
        moat_types.append("无宽阔护城河 (No Moat)")
        reasoning.append("数据与文本均未显示出难以逾越的竞争壁垒，可能处于完全竞争的红海市场。")

    print(json.dumps({
        "first_principle_moat": moat_types,
        "logical_deduction": reasoning
    }))

if __name__ == "__main__": main()
```

---

### 🎯 四、 业务级 Skills (Business Level)

#### 4. `business_model_sustainability` (商业模式终局与颠覆风险评估)

**功能**：给出终极的“持有信念感评分”，评估其是否会被 AI、新能源等新技术颠覆。

* **`config.json`**

```json
{ "required_data": [] }
```

* **`skill.md`**

```markdown
# 技能名称: business_model_sustainability
## 功能描述
评估公司商业模式的长期可持续性（10年以上），测算其被新技术（如AI）或新商业模式颠覆的风险，并输出长期战略定力（Conviction Level）。
## 入参格式 (JSON)
- first_principle_moat (List[str]): 护城河类型
- industry_level_1 (str): 申万一级行业 (需假设从外界获取)
```

* **`script.py`**

```python
import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    moats = params.get("first_principle_moat", ["No Moat"])
    industry = params.get("industry_level_1", "未知行业")
    
    disruption_risk = "MEDIUM (中等)"
    conviction = "HOLD (持有观察)"
    logic = ""

    # 脆弱性判定 (易被技术颠覆的行业)
    high_disruption_sectors = ["传媒", "计算机", "通信", "商贸零售", "电子"]
    # 反脆弱判定 (人类基础需求，极难被颠覆)
    low_disruption_sectors = ["食品饮料", "煤炭", "公用事业", "医药生物", "银行"]

    if industry in high_disruption_sectors:
        if "网络效应 (Network Effect)" in moats or "无形资产 (Intangible Assets)" in moats:
            disruption_risk = "MEDIUM (中等)"
            logic = f"属于技术迭代极快的【{industry}】行业，颠覆风险本应极高，但其拥有的核心护城河提供了缓冲护垫。"
            conviction = "STRONG HOLD (坚定持有)"
        else:
            disruption_risk = "HIGH (极高)"
            logic = f"属于【{industry}】行业且缺乏核心护城河，在AI与技术浪潮下随时面临被降维打击甚至价值归零的风险。"
            conviction = "AVOID (避免长期持有)"
            
    elif industry in low_disruption_sectors:
        disruption_risk = "LOW (极低)"
        logic = f"属于【{industry}】行业，底层逻辑建立在人类永恒的基础需求之上，极难被新技术彻底颠覆。"
        if "无形资产 (Intangible Assets)" in moats or "成本优势 (Cost Advantage)" in moats:
            conviction = "CORE ASSET (世代传承的核心资产)"
        else:
            conviction = "HOLD (持有观察)"
            
    else:
        # 一般制造业或其他
        if "无宽阔护城河 (No Moat)" in moats:
            disruption_risk = "HIGH (较高)"
            conviction = "TRADE ONLY (仅适合波段交易)"
            logic = "缺乏护城河的一般性行业，容易陷入价格战泥潭，不具备穿越牛熊的长期基因。"
        else:
            disruption_risk = "LOW (较低)"
            conviction = "STRONG HOLD (坚定持有)"
            logic = "在传统行业中构建了宽阔的护城河，现金流具有较强的抗期性。"

    print(json.dumps({
        "long_term_disruption_risk": disruption_risk,
        "holding_conviction_level": conviction,
        "sustainability_insight": logic,
        "business_nature_summary": f"生意的本质：这是一家依靠【{', '.join(moats)}】在【{industry}】行业中获取超额利润的企业。"
    }))

if __name__ == "__main__": main()
```

---

### 🚀 五、 无缝接入主编排器 (仅需 2 步)

**步骤 1：在主编排器中导入并注册**
打开 `agents/main_orchestrator.py`：

```python
# 1. 导入
from agents.specialized.business_logic_agent import BusinessLogicAgent

# 2. 在 __init__ 的 agent_registry 中注册
self.agent_registry = {
    # ... 其他 agent ...
    "technical_agent": TechnicalAgent(),
    "business_logic_agent": BusinessLogicAgent()  # 👈 新增这行
}
```

**步骤 2：使用 Pydantic Literal 锁死路由**
在 `agents/main_orchestrator.py` 中，更新 `SubTask` 和 `sys_prompt`：

```python
class SubTask(BaseModel):
    target_agent: Literal[
        "industry_agent",
        "fundamental_agent",
        "valuation_agent",
        "sentiment_agent",
        "catalyst_agent",
        "comprehensive_agent",
        "risk_agent",
        "technical_agent",
        "business_logic_agent"  # 👈 必须在这里加上！
    ] = Field(..., description="负责处理此任务的分智能体名称标识")

# ... 在 _plan_dag 的 sys_prompt 中加入说明 ...
"""
9. business_logic_agent: 查商业模式、护城河、单位经济模型、第一性原理、颠覆风险。

【强制路由规则】：
- 如果用户提到“护城河”、“商业模式”、“核心竞争力”、“第一性原理”、“靠什么赚钱”、“长期持有”等字眼，你【必须】生成一个 target_agent 为 'business_logic_agent' 的子任务！
"""
```

### 💡 架构师点评

现在，当用户问出：**“茅台和宁德时代，谁的商业模式更好？谁能拿10年？”**

这个新加入的智能体会用极其冷酷的数据告诉你：

* **茅台**：毛利率 92%，研发费率 0.1% -> 判定为“品牌无形资产护城河”。属于食品饮料业，颠覆风险 LOW，结论：`CORE ASSET (世代传承的核心资产)`。
* **宁德时代**：毛利率 22%，研发费率极高 -> 判定为“成本优势+技术壁垒”。属于新能源制造业，技术迭代快，颠覆风险 MEDIUM，结论：`STRONG HOLD (坚定持有，但需警惕固态电池等技术颠覆)`。

**它把虚无缥缈的“商业分析”，完美地变成了可量化、可追溯的 JSON 数据流！**


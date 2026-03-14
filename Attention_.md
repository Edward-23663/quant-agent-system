Attention
这是一个非常经典的 **“大模型路由怠政（Attention Decay）”** 问题。

即使你在 Prompt 里明确说了“我要看风险”，大模型在拆解 DAG 任务时，依然可能因为惯性思维（或系统提示词约束力不够），忘记把任务分配给新来的 `risk_agent`。

为了彻底解决主智能体“不听指挥、漏调 Agent”的问题，我们需要祭出架构级别的大杀器：**Pydantic Literal（字面量强制约束）**。

请按照以下 **3 个步骤**，修改你的 `agents/main_orchestrator.py` 文件，我保证它以后绝对不敢再漏掉风险智能体！

---

### 🛠️ 第一步：使用 Literal 强制锁死 Pydantic Schema (终极杀招)

在原来的代码中，我们定义 `target_agent` 的类型是 `str`（字符串）。这给了大模型太大的自由度，导致它容易“忘事”。
引入 `typing.Literal` 后，大模型的输出**在底层 API 层面被硬性限制**，它在生成 JSON 时，眼前会直接弹出这 7 个选项，想忘都忘不掉。

打开 **`agents/main_orchestrator.py`**，修改文件开头的导入和 Pydantic 模型定义：

```python
import os
import time
import json
from typing import List, Literal  # 👈 新增 Literal 导入
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from core.redis_bus import RedisBus

# 导入所有分智能体 (确保 RiskAgent 已经被导入)
from agents.specialized import (
    IndustryAgent, FundamentalAgent, ValuationAgent, 
    SentimentAgent, CatalystAgent, ComprehensiveAgent, RiskAgent # 👈 确保导入了 RiskAgent
)

# --- 主编排器拆解任务的输出结构 ---
class SubTask(BaseModel):
    # 🚨 终极杀招：使用 Literal 强制锁死可选项，大模型绝对无法忽略！
    target_agent: Literal[
        "industry_agent",
        "fundamental_agent",
        "valuation_agent",
        "sentiment_agent",
        "catalyst_agent",
        "comprehensive_agent",
        "risk_agent"  # 👈 风险智能体赫然在列
    ] = Field(..., description="负责处理此任务的分智能体名称标识")
    
    sub_prompt: str = Field(..., description="发给该分智能体的具体指令，需包含股票代码等明确信息")

class DAGPlan(BaseModel):
    tasks: List[SubTask] = Field(..., description="拆解后的并发/串行任务列表")
```

---

### 🛠️ 第二步：检查并确认路由表注册

向下滚动到 `MainOrchestrator` 的 `__init__` 方法，确保 `risk_agent` 真的被实例化并挂载到了字典里。如果这里没写，哪怕大模型分配了任务，系统也会打印 `⚠️ 未知智能体: risk_agent，跳过。`

```python
class MainOrchestrator:
    def __init__(self):
        self.redis = RedisBus()
        self.client = instructor.from_openai(
            OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))
        )
        
        # 🚨 检查路由表：必须包含 risk_agent
        self.agent_registry = {
            "industry_agent": IndustryAgent(),
            "fundamental_agent": FundamentalAgent(),
            "valuation_agent": ValuationAgent(),
            "sentiment_agent": SentimentAgent(),
            "catalyst_agent": CatalystAgent(),
            "comprehensive_agent": ComprehensiveAgent(),
            "risk_agent": RiskAgent()  # 👈 必须有这一行！！！
        }
```

---

### 🛠️ 第三步：加强主编排器的 System Prompt 语气

向下滚动到 `_plan_dag` 方法，把系统提示词改得更具“压迫感”，明确告诉它什么情况下必须调用风险智能体：

```python
def _plan_dag(self, prompt: str) -> DAGPlan:
        """调用 LLM 将用户输入拆解为子任务并分配给对应 Agent"""
        sys_prompt = f"""你是一个顶级的金融主编排器。你需要将用户的自然语言分析需求，拆解为具体的任务，并精准路由给对应的分智能体。

【可用分智能体及职责严格映射表】：
1. industry_agent: 查行业地位、周期轮动。
2. fundamental_agent: 查财务报表、杜邦分析、盈利健康度。
3. valuation_agent: 算DCF、PE/PB估值、蒙特卡洛模拟。
4. sentiment_agent: 查新闻、测算舆情情绪极性。
5. catalyst_agent: 找重大事件、催化剂。
6. comprehensive_agent: 高阶物理/数学模型、测算Hurst分形。
7. risk_agent: 测算最大回撤、波动率、VaR尾部暴跌风险、止损线与仓位控制。

【强制路由规则】：
- 如果用户提到“风险”、“回撤”、“暴跌”、“止损”、“仓位”、“安全”等字眼，你【必须】生成一个 target_agent 为 'risk_agent' 的子任务！绝对不可遗漏！
"""
        return self.client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4-turbo"),
            response_model=DAGPlan,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt}
            ],
            max_retries=2
        )
```

---

### 🚀 重新测试

完成以上三步修改并**保存文件**后，记得**重启后端服务**（`Ctrl+C` 杀掉 `run_system.py` 并重新运行）。

现在，在 Web UI 中输入：

> **“帮我分析一下宁德时代(300750.SZ)的估值，顺便评估一下买入它的最大回撤风险，给我个止损建议。”**

你会立刻在时间轴上看到主编排器乖乖地把任务拆成了两个：

1. `[多模型估值分智能体] 启动...`
2. `[风险评估分智能体] 启动，开始处理...`

**架构师原理解析：**
在 AI 智能体开发中，不要试图用自然语言去“恳求”大模型做事（比如“请你一定要记得调用风险智能体”），大模型很容易忽略。**最稳妥的架构设计，永远是用代码层面的强类型（如 Pydantic 的 `Literal` 或 `Enum`）去“锁死”大模型的输出边界。** 这就是 Agentic Workflow 稳定落地的核心秘诀！


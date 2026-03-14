# agents/main_orchestrator.py
import os
import re
import time
import json
from typing import List, Literal, Set
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from dotenv import load_dotenv
from core.redis_bus import RedisBus

load_dotenv()

from agents.specialized import (
    IndustryAgent, FundamentalAgent, ValuationAgent,
    SentimentAgent, CatalystAgent, ComprehensiveAgent, RiskAgent, TechnicalAgent, BusinessLogicAgent
)

VALID_AGENTS = {
    "industry_agent", "fundamental_agent", "valuation_agent",
    "sentiment_agent", "catalyst_agent", "risk_agent", "comprehensive_agent", "technical_agent", "business_logic_agent"
}

TICKER_PATTERN = re.compile(r'(\d{6}[.SH]|SZ\d{6})')


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
        "business_logic_agent"
    ] = Field(..., description="负责处理此任务的分智能体名称标识")
    
    sub_prompt: str = Field(..., description="发给该分智能体的具体指令，需包含股票代码等明确信息")


class DAGPlan(BaseModel):
    tasks: List[SubTask] = Field(..., description="拆解后的并发/串行任务列表")


class MainOrchestrator:
    def __init__(self):
        self.redis = RedisBus()
        self.client = instructor.from_openai(
            OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))
        )
        
        self.agent_registry = {
            "industry_agent": IndustryAgent(),
            "fundamental_agent": FundamentalAgent(),
            "valuation_agent": ValuationAgent(),
            "sentiment_agent": SentimentAgent(),
            "catalyst_agent": CatalystAgent(),
            "comprehensive_agent": ComprehensiveAgent(),
            "risk_agent": RiskAgent(),
            "technical_agent": TechnicalAgent(),
            "business_logic_agent": BusinessLogicAgent()
        }

    def _extract_ticker(self, prompt: str) -> str:
        """从用户输入提取股票代码"""
        match = TICKER_PATTERN.search(prompt.upper())
        if match:
            code = match.group(1)
            return code.replace('SZ', '') if code.startswith('SZ') else code
        return "UNKNOWN"

    def _normalize_prompt(self, prompt: str, ticker: str) -> str:
        """标准化 prompt，确保包含股票代码"""
        if ticker and ticker not in prompt:
            return f"{prompt} {ticker}"
        return prompt

    def _deduplicate_tasks(self, tasks: List[SubTask]) -> List[SubTask]:
        """去除重复的智能体调用，保留第一个"""
        seen: Set[str] = set()
        unique_tasks = []
        for task in tasks:
            if task.target_agent not in seen:
                seen.add(task.target_agent)
                unique_tasks.append(task)
        return unique_tasks

    def _validate_tasks(self, tasks: List[SubTask]) -> List[SubTask]:
        """验证任务有效性，过滤无效智能体"""
        valid_tasks = []
        for task in tasks:
            if task.target_agent not in VALID_AGENTS:
                continue
            valid_tasks.append(task)
        return valid_tasks

    def run_workflow(self, task_id: str, user_prompt: str):
        """主工作流入口"""
        ticker = self._extract_ticker(user_prompt)
        
        self.redis.publish_status(task_id, "👑 [主编排器] 接收到用户请求，正在拆解任务 DAG...")
        
        dag_plan = self._plan_dag(user_prompt)
        
        dag_plan.tasks = self._deduplicate_tasks(dag_plan.tasks)
        dag_plan.tasks = self._validate_tasks(dag_plan.tasks)
        
        self.redis.publish_status(task_id, f"👑 [主编排器] 任务拆解完成，共 {len(dag_plan.tasks)} 个子任务: {[t.target_agent for t in dag_plan.tasks]}")

        final_reports = []
        executed_agents: Set[str] = set()

        for task in dag_plan.tasks:
            if task.target_agent in executed_agents:
                self.redis.publish_status(task_id, f"⚠️ 跳过重复任务: {task.target_agent}")
                continue
                
            agent_instance = self.agent_registry.get(task.target_agent)
            if not agent_instance:
                self.redis.publish_status(task_id, f"⚠️ 未知智能体: {task.target_agent}，跳过。")
                continue
            
            executed_agents.add(task.target_agent)
            normalized_prompt = self._normalize_prompt(task.sub_prompt, ticker)
            
            while True:
                response = agent_instance.execute(task_id, normalized_prompt)
                
                if response["status"] == "SUCCESS":
                    final_reports.append(f"### {agent_instance.agent_name} 报告\n{response['result']}")
                    break
                    
                elif response["status"] == "SUSPENDED":
                    self.redis.publish_status(task_id, f"👑 [主编排器] 获悉 {agent_instance.agent_name} 挂起，进入后台监听...")
                    
                    pubsub = self.redis.client.pubsub()
                    pubsub.subscribe(f"task_status:{task_id}")
                    
                    for message in pubsub.listen():
                        if message['type'] == 'message':
                            data = message['data']
                            if "SYSTEM_SIGNAL:DATA_READY" in data:
                                self.redis.publish_status(task_id, "👑 [主编排器] 收到数据就绪信号！正在重新唤醒分智能体 🚀")
                                pubsub.unsubscribe()
                                pubsub.close()
                                break
                    time.sleep(1)
                    
                else:
                    self.redis.publish_status(task_id, f"❌ {agent_instance.agent_name} 任务失败。")
                    break

        self.redis.publish_status(task_id, "👑 [主编排器] 所有分智能体任务完毕，正在进行终局报告合成...")
        final_markdown = "\n\n".join(final_reports)
        
        self._call_main_skills(task_id, final_markdown)

        self.redis.publish_status(task_id, "🎉 [主编排器] 整体工作流圆满结束！")
        self.redis.publish_status(task_id, f"FINAL_RESULT:{final_markdown}")

    def _plan_dag(self, prompt: str) -> DAGPlan:
        """调用 LLM 将用户输入拆解为子任务并分配给对应 Agent"""
        full_analysis_keywords = ["全面分析", "完整分析", "综合分析", "全面评估", "完整评估", "full analysis", "comprehensive", "风险评估", "帮我分析风险"]
        is_full_analysis = any(kw in prompt.lower() for kw in full_analysis_keywords)
        
        if is_full_analysis:
            return DAGPlan(tasks=[
                SubTask(target_agent="fundamental_agent", sub_prompt=prompt),
                SubTask(target_agent="valuation_agent", sub_prompt=prompt),
                SubTask(target_agent="sentiment_agent", sub_prompt=prompt),
                SubTask(target_agent="industry_agent", sub_prompt=prompt),
                SubTask(target_agent="catalyst_agent", sub_prompt=prompt),
                SubTask(target_agent="risk_agent", sub_prompt=prompt),
                SubTask(target_agent="technical_agent", sub_prompt=prompt),
                SubTask(target_agent="business_logic_agent", sub_prompt=prompt),
                SubTask(target_agent="comprehensive_agent", sub_prompt=prompt),
            ])
        
        sys_prompt = f"""你是一个顶级的金融主编排器。你需要将用户的自然语言分析需求，拆解为精准的任务，并路由给对应的分智能体。

【可用分智能体及职责严格映射表】：
1. industry_agent: 查行业地位、周期轮动。
2. fundamental_agent: 查财务报表、杜邦分析、盈利健康度。
3. valuation_agent: 算DCF、PE/PB估值、蒙特卡洛模拟。
4. sentiment_agent: 查新闻、测算舆情情绪极性。
5. catalyst_agent: 找重大事件、催化剂。
6. comprehensive_agent: 高阶物理/数学模型、测算Hurst分形。
7. risk_agent: 测算最大回撤、波动率、VaR尾部暴跌风险、止损线与仓位控制。
8. technical_agent: 查技术面、量价背离、均线/MACD/KDJ指标、找支撑阻力位与买卖点。
9. business_logic_agent: 查商业模式、护城河、单位经济模型、第一性原理、颠覆风险。

【强制路由规则】（每个智能体3个关键词，精确匹配）：
- 包含"风险"、"止损"、"回撤" → 必须调用 risk_agent
- 包含"估值"、"价值"、"PE" → 必须调用 valuation_agent
- 包含"基本面"、"财报"、"ROE" → 必须调用 fundamental_agent
- 包含"行业"、"板块"、"持仓" → 必须调用 industry_agent
- 包含"舆情"、"情绪"、"新闻" → 必须调用 sentiment_agent
- 包含"催化剂"、"利好"、"利空" → 必须调用 catalyst_agent
- 包含"综合"、"宏观"、"长期" → 必须调用 comprehensive_agent
- 包含"技术面"、"买卖点"、"支撑位"、"阻力位"、"均线"、"MACD"、"放量" → 必须调用 technical_agent
- 包含"护城河"、"商业模式"、"核心竞争力"、"第一性原理"、"靠什么赚钱"、"长期持有" → 必须调用 business_logic_agent

【规则】：如果用户输入同时涉及多个领域，可以分配多个子任务。关键词优先级高于其他判断。"""

        model = os.getenv("LLM_MODEL", "gpt-4-turbo")
        return self.client.chat.completions.create(
            model=model,
            response_model=DAGPlan,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt}
            ]
        )

    def _call_main_skills(self, task_id: str, markdown_content: str):
        """调用主编排器专属技能卡带 (如 PDF 导出)"""
        self.redis.publish_status(task_id, "👑 [主编排器] 正在调用技能卡带 `atomic_pdf_export` 渲染 PDF 文件...")
        time.sleep(2)
        self.redis.publish_status(task_id, "👑 [主编排器] PDF 研报生成完毕，已保存至本地 output/ 目录。")

# agents/specialized/sentiment_agent.py
from agents.base_sub_agent import BaseSubAgent


class SentimentAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_name="舆情分析分智能体",
            role_desc="""你负责从 RAG 本地向量库召回相关新闻与公告，使用 FinBERT 进行情感极性打分，计算社交媒体讨论热度指数，分析舆情与股价波动的时序关联，评估舆情黑天鹅风险等级。

【重要指令】：
1. 你必须【一步一步、按顺序】调用技能，每次只能调用一个技能。
2. 拿到上一个技能的结果后，再决定调用下一个技能。
3. 当收集到足够数据后，将 is_final_answer 设为 true，并输出 Markdown 格式的分析报告。""",
            skills_dir="skills/sub_skills/sentiment_agent"
        )

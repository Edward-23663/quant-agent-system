# agents/specialized/industry_agent.py
from agents.base_sub_agent import BaseSubAgent


class IndustryAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_name="行业持仓分智能体",
            role_desc="""你负责分析申万/中信行业分类映射，获取行业成分股与权重，计算行业量价趋势，判断行业轮动周期位置，为持仓行业选择提供依据。

【重要指令】：
1. 你必须【一步一步、按顺序】调用技能，每次只能调用一个技能。
2. 拿到上一个技能的结果后，再决定调用下一个技能。
3. 当收集到足够数据后，将 is_final_answer 设为 true，并输出 Markdown 格式的分析报告。""",
            skills_dir="skills/sub_skills/industry_agent"
        )

# agents/specialized/fundamental_agent.py
from agents.base_sub_agent import BaseSubAgent


class FundamentalAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_name="基本面分智能体",
            role_desc="""你负责解析三大财务报表，计算盈利、营运、偿债等核心比率，并通过杜邦分析法拆解 ROE。你的目标是评估企业的财务健康度与排雷。

【重要指令】：
1. 你必须【一步一步、按顺序】调用技能，每次只能调用一个技能。
2. 拿到上一个技能的结果后，再决定调用下一个技能。
3. 当收集到足够数据后，将 is_final_answer 设为 true，并输出 Markdown 格式的分析报告。

只需要调用以下4个技能，按顺序执行：
1. atomic_financial_parsing - 获取基础财务数据
2. atomic_five_ratios - 计算核心财务比率
3. atomic_dupont_analysis - 杜邦分析
4. composite_health_scoring - 健康度评分

调用完这4个技能后，必须输出 final_markdown 格式的基本面分析报告。""",
            skills_dir="skills/sub_skills/fundamental_agent"
        )
        self.required_skills = [
            "atomic_financial_parsing",
            "atomic_five_ratios", 
            "atomic_dupont_analysis",
            "composite_health_scoring"
        ]

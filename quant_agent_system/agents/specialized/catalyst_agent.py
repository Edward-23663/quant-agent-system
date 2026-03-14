# agents/specialized/catalyst_agent.py
from agents.base_sub_agent import BaseSubAgent


class CatalystAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_name="催化剂分析分智能体",
            role_desc="""你负责提取重大合同、财报预告、政策事件等催化剂信息，量化评估事件对营收/利润的影响力度，分析催化剂事件与估值模型参数调整的关联，提供短中期催化剂清单与爆发概率评估。

【重要指令】：
1. 你必须【一步一步、按顺序】调用技能，每次只能调用一个技能。
2. 拿到上一个技能的结果后，再决定调用下一个技能。
3. 当收集到足够数据后，将 is_final_answer 设为 true，并输出 Markdown 格式的分析报告。""",
            skills_dir="skills/sub_skills/catalyst_agent"
        )

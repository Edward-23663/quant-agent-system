# agents/specialized/valuation_agent.py
from agents.base_sub_agent import BaseSubAgent


class ValuationAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_name="多模型估值分智能体",
            role_desc="""你负责使用 DCF、相对估值、蒙特卡洛等多种数学模型，对标的进行绝对客观的估值计算与交叉验证。你必须依赖底层脚本的计算结果，严禁自己编造财务数据或估值结果。

【重要指令】：
1. 你必须【一步一步、按顺序】调用技能，每次只能调用一个技能。
2. 拿到上一个技能的结果后，再决定调用下一个技能。
3. 当收集到足够数据后，将 is_final_answer 设为 true，并输出 Markdown 格式的估值报告。

只需要调用以下5个技能，按顺序执行：
1. atomic_dcf_calc - DCF现金流折现估值
2. atomic_relative_val - PE/PB历史分位数
3. atomic_monte_carlo - 蒙特卡洛模拟
4. composite_cross_valid - 交叉验证
5. business_val_range - 估值区间计算

调用完这5个技能后，必须输出 final_markdown 格式的估值分析报告，包含：目标价、估值区间，安全边际、投资建议。""",
            skills_dir="skills/sub_skills/valuation_agent"
        )
        self.required_skills = [
            "atomic_dcf_calc",
            "atomic_relative_val",
            "atomic_monte_carlo",
            "composite_cross_valid",
            "business_val_range"
        ]

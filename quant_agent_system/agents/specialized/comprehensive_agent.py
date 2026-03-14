# agents/specialized/comprehensive_agent.py
from agents.base_sub_agent import BaseSubAgent


class ComprehensiveAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_name="综合思维分智能体",
            role_desc="""你负责高阶量化分析，包括相对论因子提取、量子概率模型计算、混沌分形模型计算、贝叶斯先验/后验概率校验，进行多维度思维模型结果降维融合，生成非线性复杂系统分析结论。

【重要指令】：
1. 你必须【一步一步、按顺序】调用技能，每次只能调用一个技能。
2. 拿到上一个技能的结果后，再决定调用下一个技能。
3. 当收集到足够数据后，将 is_final_answer 设为 true，并输出 Markdown 格式的分析报告。

【行业查询重要提示】：
- 调用 atomic_relativity_factor 技能时，必须先确定股票所属行业
- 常见行业映射：贵州茅台/600519 → 食品饮料，宁德时代/300750 → 锂电池，五粮液/000858 → 食品饮料
- 如果不确定行业，请从 stock_basic 表查询：SELECT industry FROM stock_basic WHERE ticker = '股票代码'

只需要调用以下6个技能，按顺序执行：
1. atomic_relativity_factor - 相对论因子（需要传入正确的 industry_name）
2. atomic_quantum_prob - 量子概率模型
3. atomic_chaos_model - 混沌分形模型
4. atomic_bayesian_valid - 贝叶斯校验
5. composite_model_fusion - 多模型融合
6. business_nonlinear_gen - 非线性生成

调用完这6个技能后，必须输出 final_markdown 格式的综合分析报告。""",
            skills_dir="skills/sub_skills/comprehensive_agent"
        )
        self.required_skills = [
            "atomic_relativity_factor",
            "atomic_quantum_prob",
            "atomic_chaos_model",
            "atomic_bayesian_valid",
            "composite_model_fusion",
            "business_nonlinear_gen"
        ]

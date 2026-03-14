# agents/base_sub_agent.py
import os
import json
import duckdb
import subprocess
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from dotenv import load_dotenv
from core.redis_bus import RedisBus

load_dotenv()

class AgentDecision(BaseModel):
    is_final_answer: bool = Field(..., description="如果已经收集到足够信息可以回答用户，设为 true；如果需要调用技能计算，设为 false")
    skill_name: Optional[str] = Field(None, description="要调用的技能文件夹名称，如 'atomic_dcf_calc'")
    params: Optional[Dict[str, Any]] = Field(None, description="传递给底层 Python 脚本的参数字典")
    reasoning: str = Field(..., description="你的思考过程")
    final_markdown: Optional[str] = Field(None, description="如果是最终回答，这里输出专业连贯的 Markdown 分析段落")


def get_current_date():
    """动态获取当前日期，确保时间校准准确"""
    return datetime.now().strftime("%Y-%m-%d")


class BaseSubAgent:
    def __init__(self, agent_name: str, role_desc: str, skills_dir: str):
        self.agent_name = agent_name
        self.role_desc = role_desc
        self.skills_dir = skills_dir
        self.required_skills = []  # 子类可以定义必要的技能列表
        self.redis = RedisBus()
        
        self.client = instructor.from_openai(
            OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))
        )
        self.db_path = "data/db/quant_data.duckdb"

    def execute(self, task_id: str, prompt: str, max_steps: int = 20) -> Dict[str, Any]:
        current_date = get_current_date()
        self.redis.publish_status(task_id, f"[{self.agent_name}] 启动，开始处理: {prompt}")
        self.redis.publish_status(task_id, f"[{self.agent_name}] 当前校准时间: {current_date}")
        
        context_history = f"用户原始需求: {prompt}\n当前参考日期: {current_date}\n"
        skill_results = []  # 收集所有技能结果

        for step in range(max_steps):
            decision = self._think_and_decide(context_history)
            self.redis.publish_status(task_id, f"[{self.agent_name}] 思考: {decision.reasoning}")

            if decision.is_final_answer:
                if decision.final_markdown:
                    self.redis.publish_status(task_id, f"[{self.agent_name}] 结论已生成。")
                    return {"status": "SUCCESS", "result": decision.final_markdown}
                else:
                    self.redis.publish_status(task_id, f"[{self.agent_name}] 思考: 需要继续获取数据生成结论...")

            if not decision.skill_name:
                # 🚨 核心修复：如果大模型没有输出技能名，严厉警告并记入上下文，防止它陷入死循环空想
                warning_msg = f"\n[系统警告]: 你的上一步思考是 '{decision.reasoning}'，但你没有在 JSON 中指定要调用的 skill_name！请立即指定【1个】你要调用的技能，不要试图并发调用！\n"
                context_history += warning_msg
                self.redis.publish_status(task_id, f"[{self.agent_name}] ⚠️ 触发防空想机制，正在纠正大模型行为...")
                continue

            self.redis.publish_status(task_id, f"[{self.agent_name}] 决定调用技能卡带: {decision.skill_name}")
            skill_path = os.path.join(self.skills_dir, decision.skill_name)

            missing_table = self._check_data_and_suspend(skill_path, decision.params)
            if missing_table:
                self.redis.publish_status(task_id, f"[{self.agent_name}] ⛔ 拦截：发现 DuckDB 缺失表 `{missing_table}` 的数据。")
                self.redis.publish_status(task_id, f"[{self.agent_name}] 触发异步采集，当前智能体进程挂起 (休眠释放内存) 💤")
                
                self.redis.push_to_queue("data_fetch_queue", {
                    "task_id": task_id,
                    "ticker": (decision.params or {}).get('ticker', 'UNKNOWN'),
                    "table": missing_table
                })
                return {"status": "SUSPENDED", "reason": "WAITING_DATA"}

            self.redis.publish_status(task_id, f"[{self.agent_name}] 数据齐备，拉起底层硬核计算脚本...")
            try:
                raw_result = self._execute_script(skill_path, decision.params or {})
                self.redis.publish_status(task_id, f"[{self.agent_name}] 脚本执行成功，获取到纯数字结果。")
                skill_results.append({"skill": decision.skill_name, "data": raw_result})
                context_history += f"\n调用技能 {decision.skill_name} 返回结果: {json.dumps(raw_result)}\n"
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr or e.stdout or str(e)
                self.redis.publish_status(task_id, f"[{self.agent_name}] ❌ 脚本执行失败: {error_msg[:200]}")
                context_history += f"\n调用技能 {decision.skill_name} 失败: {error_msg[:200]}\n"
            except Exception as e:
                self.redis.publish_status(task_id, f"[{self.agent_name}] ❌ 脚本执行失败: {str(e)[:200]}")
                context_history += f"\n调用技能 {decision.skill_name} 失败: {str(e)[:200]}\n"

        return {"status": "FAILED", "reason": "达到最大 ReAct 思考步数"}

    def _think_and_decide(self, context: str) -> AgentDecision:
        """读取 skill.md 生成上下文，强制 LLM 输出标准化 JSON"""
        skills_info = ""
        if os.path.exists(self.skills_dir):
            for skill in os.listdir(self.skills_dir):
                skill_md_path = os.path.join(self.skills_dir, skill, "skill.md")
                if os.path.exists(skill_md_path):
                    with open(skill_md_path, "r", encoding="utf-8") as f:
                        skills_info += f"\n--- Skill: {skill} ---\n{f.read()}\n"

        sys_prompt = f"""你是一个专业的量化分析子智能体。你的角色是: {self.role_desc}。
你有以下严格物理隔离的技能卡带可以使用：
{skills_info}

【⚠️ 绝对执行红线 (必读)】：
1. 你【严禁】尝试一次性调用多个技能！每次只能挑选【1个】最急需的技能填入 skill_name。
2. 如果你需要数据，`is_final_answer` 必须设为 false，且 `skill_name` 绝对不能为空！
3. 拿到当前技能的结果后，系统会再次唤醒你，你再去调用下一个技能。必须一步一步来！
4. 当所有需要的数据都已经收集完毕，将 `is_final_answer` 设为 true，并在 `final_markdown` 中输出最终的专业研报段落。

## 输出格式要求
你必须严格按照以下 JSON 格式输出：
- is_final_answer: true 表示直接输出分析结论，false 表示需要调用技能
- skill_name: 如果 is_final_answer 为 false，填写要调用的技能文件夹名称（如 atomic_dcf_calc）
- params: 如果 is_final_answer 为 false，填写传递给技能的参数字典（如 ticker: "600519", target_date: "2023-12-31"）
- reasoning: 你的思考过程
- final_markdown: 如果 is_final_answer 为 true，填写分析结论的 Markdown 内容

请根据当前上下文，决定是调用技能获取数据，还是直接输出最终的 Markdown 分析结论。"""

        model = os.getenv("LLM_MODEL", "gpt-4-turbo")
        return self.client.chat.completions.create(
            model=model,
            response_model=AgentDecision,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": context}
            ],
            max_retries=2
        )

    def _normalize_ticker(self, ticker: str) -> str:
        """Normalize ticker format: 600519.SH -> 600519, 000001.SZ -> 000001"""
        return ticker.replace('.SH', '').replace('.SZ', '')

    def _check_data_and_suspend(self, skill_path: str, params: Optional[Dict]) -> Optional[str]:
        """读取 config.json 校验 DuckDB，返回缺失的表名，若无缺失返回 None"""
        config_path = os.path.join(skill_path, "config.json")
        if not os.path.exists(config_path):
            return None
            
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        normalized_ticker = self._normalize_ticker((params or {}).get('ticker', ''))
            
        try:
            with duckdb.connect(self.db_path, read_only=True) as db:
                for req in config.get("required_data", []):
                    table = req["table"]
                    min_records = req.get("min_records", 1)
                    try:
                        has_ticker_col = False
                        try:
                            col_check = db.execute(f"SELECT ticker FROM {table} LIMIT 1").fetchone()
                            has_ticker_col = True
                        except:
                            pass
                        
                        if has_ticker_col and normalized_ticker:
                            count = db.execute(f"SELECT COUNT(*) FROM {table} WHERE ticker = ?", (normalized_ticker,)).fetchone()[0]
                            if count < min_records:
                                return table
                        else:
                            result = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                            count = result[0] if result else 0
                            if count < min_records:
                                return table
                    except duckdb.CatalogException:
                        return table
        except Exception as e:
            logging.error(f"DuckDB 校验异常: {e}, skill_path={skill_path}")
            return "unknown_table"
            
        return None

    def _execute_script(self, skill_path: str, params: Dict) -> Dict:
        """通过 subprocess 隔离执行纯 Python 脚本"""
        script_file = os.path.join(skill_path, "script.py")
        env = os.environ.copy()
        
        normalized_params = (params or {}).copy()
        if 'ticker' in normalized_params:
            normalized_params['ticker'] = self._normalize_ticker(normalized_params['ticker'])
        
        normalized_params['target_date'] = get_current_date()
        
        env["SKILL_PARAMS"] = json.dumps(normalized_params)
        
        result = subprocess.run(
            ["python", script_file],
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    def _generate_auto_report(self, skill_results: list, params: Dict) -> str:
        """当 LLM 无法生成报告时，自动从技能结果拼接报告"""
        ticker = params.get('ticker', 'UNKNOWN')
        
        report = f"# {ticker} 分析报告\n\n"
        
        for item in skill_results:
            skill_name = item.get('skill', '')
            data = item.get('data', {})
            
            if skill_name == 'atomic_financial_parsing':
                report += f"## 基础财务数据\n"
                report += f"- 营收: {data.get('total_revenue', 'N/A'):,.0f} 元\n"
                report += f"- 净利润: {data.get('net_profit', 'N/A'):,.0f} 元\n"
                report += f"- 自由现金流: {data.get('free_cash_flow', 'N/A'):,.0f} 元\n"
                report += f"- 总资产: {data.get('total_assets', 'N/A'):,.0f} 元\n"
                report += f"- 总负债: {data.get('total_liabilities', 'N/A'):,.0f} 元\n"
                report += f"- 股东权益: {data.get('total_equity', 'N/A'):,.0f} 元\n\n"
            
            elif skill_name == 'atomic_five_ratios':
                report += f"## 核心财务比率\n"
                report += f"- ROE: {data.get('roe_pct', 'N/A')}%\n"
                report += f"- ROA: {data.get('roa_pct', 'N/A')}%\n"
                report += f"- 净利率: {data.get('net_profit_margin_pct', 'N/A')}%\n"
                report += f"- 资产负债率: {data.get('debt_to_asset_pct', 'N/A')}%\n"
                report += f"- 营收增速: {data.get('revenue_growth_pct', 'N/A')}%\n\n"
            
            elif skill_name == 'atomic_dupont_analysis':
                report += f"## 杜邦分析\n"
                dupont = data.get('dupont_components', {})
                report += f"- 净利率: {dupont.get('net_profit_margin', 'N/A')}\n"
                report += f"- 资产周转率: {dupont.get('asset_turnover', 'N/A')}\n"
                report += f"- 权益乘数: {dupont.get('equity_multiplier', 'N/A')}\n"
                report += f"- 核心驱动: {data.get('core_driver', 'N/A')}\n\n"
            
            elif skill_name == 'composite_health_scoring':
                report += f"## 健康度评分\n"
                report += f"- 得分: {data.get('raw_score', 'N/A')}\n"
                report += f"- 状态: {data.get('health_status', 'N/A')}\n"
                details = data.get('scoring_details', [])
                if details:
                    report += "- 详情:\n"
                    for d in details:
                        report += f"  - {d}\n"
                report += "\n"
            
            elif skill_name == 'atomic_dcf_calc':
                report += f"## DCF 估值\n"
                report += f"- 每股价值: {data.get('per_share_value', 'N/A')} 元\n"
                report += f"- 当前股价: {data.get('current_price', 'N/A')} 元\n"
                report += f"- WACC: {data.get('wacc', 'N/A')}\n"
                report += f"- 永续增长率: {data.get('perpetual_growth_rate', 'N/A')}\n\n"
            
            elif skill_name == 'atomic_relative_val':
                report += f"## 相对估值\n"
                report += f"- PE: {data.get('pe', 'N/A')}\n"
                report += f"- PE分位数: {data.get('pe_percentile', 'N/A')}%\n"
                report += f"- PB: {data.get('pb', 'N/A')}\n"
                report += f"- PB分位数: {data.get('pb_percentile', 'N/A')}%\n\n"
            
            elif skill_name == 'atomic_monte_carlo':
                report += f"## 蒙特卡洛模拟\n"
                report += f"- 中位数: {data.get('median', 'N/A')} 元\n"
                report += f"- P5: {data.get('p5', 'N/A')} 元\n"
                report += f"- P95: {data.get('p95', 'N/A')} 元\n\n"
            
            elif skill_name == 'composite_cross_valid':
                report += f"## 交叉验证\n"
                report += f"- 离散度: {data.get('divergence_cv', 'N/A')}\n"
                report += f"- 可靠性评分: {data.get('reliability_score', 'N/A')}\n"
                if data.get('has_logic_conflict'):
                    report += f"- 逻辑冲突: {data.get('conflict_analysis', 'N/A')}\n"
                report += "\n"
        
        return report

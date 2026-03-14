# core/exceptions.py

class QuantSystemError(Exception):
    """金融量化智能体系统全局基础异常类"""
    pass

class DataMissingError(QuantSystemError):
    """
    数据缺失异常 (核心红线)
    当 DuckDB 中不存在所需表，或数据条数/时间窗口不满足 config.json 校验要求时抛出。
    引擎捕获此异常后，将触发 Agent 挂起与异步采集机制。
    """
    def __init__(self, table_name: str, message: str = "Required data is missing."):
        self.table_name = table_name
        self.message = f"[{table_name}] {message}"
        super().__init__(self.message)

class SkillExecutionError(QuantSystemError):
    """
    技能执行异常
    当底层 script.py (纯 Python 计算逻辑) 崩溃或返回非 JSON 格式时抛出。
    """
    pass

class LLMFormatError(QuantSystemError):
    """
    大模型格式异常
    当 LLM 经过多次重试依然无法输出符合 Pydantic Schema 的 JSON 时抛出。
    """
    pass

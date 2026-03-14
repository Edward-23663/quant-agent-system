# core/llm_adapter.py
import os
import logging
from typing import Type, TypeVar, Any
from pydantic import BaseModel
import instructor
from openai import OpenAI
from dotenv import load_dotenv
from .exceptions import LLMFormatError

load_dotenv()

logger = logging.getLogger(__name__)

# 泛型 T，必须是 Pydantic 的 BaseModel 子类
T = TypeVar('T', bound=BaseModel)

class LLMAdapter:
    """
    LLM 统一适配器
    强制拦截并校验大模型的输出，确保其严格符合 Pydantic Schema。
    """
    def __init__(self, model_name: str = "gpt-4-turbo"):
        # 从环境变量获取配置，兼容 OpenAI 或本地 vLLM/Ollama 接口
        self.api_key = os.getenv("OPENAI_API_KEY", "your_api_key_here")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model_name = os.getenv("LLM_MODEL", model_name)
        
        # 普通 OpenAI 客户端 (用于文本生成)
        self._openai_client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        
        # 使用 instructor 魔法修饰 OpenAI 客户端 (用于结构化输出)
        self.client = instructor.from_openai(
            OpenAI(api_key=self.api_key, base_url=self.base_url)
        )

    def generate_structured(self, 
                            response_model: Type[T], 
                            system_prompt: str, 
                            user_prompt: str, 
                            max_retries: int = 2) -> T:
        """
        强制生成结构化 JSON 数据
        :param response_model: Pydantic 模型类
        :param system_prompt: 系统提示词
        :param user_prompt: 用户输入或上下文
        :param max_retries: 失败自动重试次数
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                response_model=response_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_retries=max_retries
            )
            return response
        except Exception as e:
            logger.error(f"LLM 结构化输出失败 (已重试 {max_retries} 次): {e}")
            raise LLMFormatError(f"无法生成符合 {response_model.__name__} 规范的数据。")

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        生成纯文本 (用于最终生成 Markdown 研报段落，不需要 JSON 校验)
        """
        try:
            response = self._openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 文本生成失败: {e}")
            return "分析报告生成失败，请检查 LLM 服务连接。"

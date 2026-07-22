#deepseek调用

from langchain_deepseek import ChatDeepSeek
from config import get_settings


settings = get_settings()

def get_llm(model: str = None, temperature: float = None):
    #获取deepseek实例
    return ChatDeepSeek(
        model=model or settings.model_name,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=temperature if temperature is not None else settings.temperature,

    )
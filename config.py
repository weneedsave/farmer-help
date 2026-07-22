from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """应用配置,自动从.env文件读取"""
    #Deepseekapi
    deepseek_api_key: str
    deepseek_base_url: str =  "https://api.deepseek.com"
    #数据库
    sqlite_path: str = "./farmer_help.db"
    chroma_persist_dir: str = "./chroma_db"
    #文件上传
    upload_dir: str = "./uploads"
    #LLM参数
    model_name: str = "deepseek-v4-flash"
    temperature: float = 0.3

    #Embedding
    embedding_model_name: str = "deepseek-v4-flash"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings()-> Settings:
    """获取配置"""
    return Settings()
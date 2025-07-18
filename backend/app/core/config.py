from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # MongoDB 설정
    MONGODB_URL: str = "mongodb://admin:password@mongodb:27017/goalmaster?authSource=admin"
    
    # OpenAI API 설정
    OPENAI_API_KEY: str = ""
    
    # JWT 설정
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    # CORS 설정
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3001"]
    
    # Redis 설정
    REDIS_URL: str = "redis://redis:6379"
    
    # 환경 설정
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings() 
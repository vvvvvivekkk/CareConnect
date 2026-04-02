from pydantic_settings import BaseSettings
from typing import Optional, Union
from pathlib import Path

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "CareConnect"
    DEBUG: Union[bool, str] = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./careconnect.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # OpenAI
    OPENAI_API_KEY: str = "your-openai-api-key-here"
    
    # File Upload - use path relative to app directory
    UPLOAD_DIR: str = str(Path(__file__).parent / "uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = str(Path(__file__).parent / ".env")
        extra = "ignore"

settings = Settings()

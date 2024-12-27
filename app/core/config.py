from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Users API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    # Generate a secure secret key if not provided
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FAKE_API_BASE_URL: str = "https://api-onecloud.multicloud.tivit.com/fake"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()

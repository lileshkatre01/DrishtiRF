from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "DrishtiRF"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "dev_secret_key_change_in_production_12345"
    
    DATABASE_URL: str = "sqlite:///./drishtirf.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    STORAGE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage")
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

settings = Settings()

os.makedirs(os.path.join(settings.STORAGE_DIR, "uploads"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "artifacts"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "reports"), exist_ok=True)

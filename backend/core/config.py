from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
import sys

def get_default_storage_dir() -> str:
    if hasattr(sys, '_MEIPASS'):
        app_data = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(app_data, "DrishtiRF", "storage")
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage")

def get_default_db_url() -> str:
    if hasattr(sys, '_MEIPASS'):
        app_data = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
        db_dir = os.path.join(app_data, "DrishtiRF")
        os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, 'drishtirf.db').replace("\\", "/")
        return f"sqlite:///{db_path}"
    return "sqlite:///./drishtirf.db"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "DrishtiRF"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "dev_secret_key_change_in_production_12345"
    
    DATABASE_URL: str = get_default_db_url()
    REDIS_URL: str = "redis://localhost:6379/0"
    
    STORAGE_DIR: str = get_default_storage_dir()
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "*"
    ]

settings = Settings()

os.makedirs(os.path.join(settings.STORAGE_DIR, "uploads"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "artifacts"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "reports"), exist_ok=True)


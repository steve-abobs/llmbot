import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    telegram_token: str = os.getenv("TELEGRAM_TOKEN", "")
    google_credentials_path: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials/service_account.json")
    google_calendar_id: str = os.getenv("GOOGLE_CALENDAR_ID", "")
    google_sheets_id: str = os.getenv("GOOGLE_SHEETS_ID", "")
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
    memory_path: str = os.getenv("MEMORY_PATH", "./data/memory.json")
    faiss_index_path: str = os.getenv("FAISS_INDEX_PATH", "./data/faiss/index.faiss")
    faiss_meta_path: str = os.getenv("FAISS_META_PATH", "./data/faiss/meta.json")


_settings: Optional[Settings] = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

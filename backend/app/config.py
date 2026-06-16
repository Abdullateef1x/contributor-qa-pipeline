from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    sync_database_url: str
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "contributor-qa-files"
    r2_endpoint_url: str = ""
    groq_api_key: str = ""
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "dev-secret-key"
    environment: str = "development"
    frontend_url: Optional[str] = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")





settings = Settings()

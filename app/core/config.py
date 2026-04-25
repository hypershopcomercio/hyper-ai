import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Mercado Livre

    # Mercado Livre
    MELI_APP_ID: str
    MELI_CLIENT_SECRET: str
    MELI_REDIRECT_URI: str | None = None
    MELI_ACCESS_TOKEN: str | None = None
    MELI_REFRESH_TOKEN: str | None = None
    MELI_USER_ID: str | None = None

    # Tiny ERP
    TINY_API_TOKEN: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"DEBUG: Loaded DATABASE_URL: {self.DATABASE_URL}")
        if not self.DATABASE_URL:
             # Default to local sqlite if nothing is provided
             self.DATABASE_URL = "sqlite:///hyper_sync.db"
             print("WARNING: No DATABASE_URL found. Defaulting to local SQLite.")


settings = Settings()

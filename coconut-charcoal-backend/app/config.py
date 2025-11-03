# app/config.py
from __future__ import annotations
from pydantic_settings import BaseSettings  # ✅ Fix here (not pydantic.BaseSettings)
from pydantic import AnyHttpUrl
from typing import List


class Settings(BaseSettings):
    # Mongo / Database
    MONGODB_URI: str
    MONGODB_DB: str = "charcoal"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Scraper
    SCRAPE_SOURCE_URL: AnyHttpUrl

    # Browser headers
    HTTP_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"   # ✅ Prevent "extra_forbidden" validation errors


settings = Settings()

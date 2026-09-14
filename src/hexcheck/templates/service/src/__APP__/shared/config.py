"""El único sitio que lee el entorno (regla H008)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="__APP_UPPER___", env_file=".env", extra="ignore")

    db_path: str = "data/__APP__.db"
    token: str = ""  # obligatorio: main.build_app falla si está vacío
    version: str = "dev"

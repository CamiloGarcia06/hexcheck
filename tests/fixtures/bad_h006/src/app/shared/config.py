import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_path: str


def load() -> Settings:
    return Settings(db_path=os.environ.get('APP_DB_PATH', 'data/app.db'))

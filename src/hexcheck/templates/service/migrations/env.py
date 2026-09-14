"""Entorno de Alembic: síncrono, SQLite, batch mode.

La URL sale de `sqlalchemy.url` si alguien la fijó (los tests lo hacen) y, si no,
de __APP_UPPER___DB_PATH. Los modelos de cada funcionalidad se importan solos para
que `--autogenerate` los vea sin editar este archivo al añadir funcionalidades.
"""

from __future__ import annotations

import importlib
import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

from __APP__.shared.db import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

if not config.get_main_option("sqlalchemy.url"):
    db_path = os.environ.get("__APP_UPPER___DB_PATH", "data/__APP__.db")
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)  # SQLite no crea carpetas
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

_src = Path(__file__).resolve().parents[1] / "src" / "__APP__"
for models in sorted(_src.glob("*/infrastructure/db/models.py")):
    feature = models.parents[2].name
    importlib.import_module(f"__APP__.{feature}.infrastructure.db.models")

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, render_as_batch=True
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

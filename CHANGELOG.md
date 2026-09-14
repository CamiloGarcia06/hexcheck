# Changelog

## v0.1.0 — 2026-09-13

- Reglas H001-H010 y W001, con un fixture por regla.
- `hexcheck new <servicio>`: esqueleto completo (uv, Taskfile, Dockerfile, Alembic, CI, `/health`, token de escritura).
- `hexcheck add <funcionalidad>`: hexágono con entidad, puerto, dos casos de uso, router, repositorio SQL, migración, fakes y tests de contrato; cablea `main.py` y `tests/conftest.py`.
- Excepciones explícitas en `[tool.hexcheck] allow`.
- Salida `--format github` y modo `--warn`.

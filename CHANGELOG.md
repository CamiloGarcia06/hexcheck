# Changelog

## v0.2.0 — 2026-09-14

Lo aprendido desplegando `tareas` y migrando claude-fluent al estándar.

- Plantilla `ci.yml`: el job `deploy` llama a `~/srv/bin/deploy` como `camilo-cachy` vía `sudo -u` (el runner no toca `~/srv` con su propio usuario).
- Errores: `shared/errors.py` gana `Unavailable` (503) y `Upstream` (502); `api_errors.py` es una tabla ordenada por familia y cada servicio nuevo trae `tests/test_api_errors.py`, que la fija (en claude-fluent un traductor desactualizado devolvió códigos equivocados sin que fallara ningún test).
- `task deploy` depende de `task check`.
- El `CLAUDE.md` generado incluye dos reglas: nada de desplegar sin `check` en verde, y releer el diff tras `ruff --fix`.
- README: funcionalidades de infraestructura pura y la tabla de errores.

## v0.1.0 — 2026-09-13

- Reglas H001-H010 y W001, con un fixture por regla.
- `hexcheck new <servicio>`: esqueleto completo (uv, Taskfile, Dockerfile, Alembic, CI, `/health`, token de escritura).
- `hexcheck add <funcionalidad>`: hexágono con entidad, puerto, dos casos de uso, router, repositorio SQL, migración, fakes y tests de contrato; cablea `main.py` y `tests/conftest.py`.
- Excepciones explícitas en `[tool.hexcheck] allow`.
- Salida `--format github` y modo `--warn`.

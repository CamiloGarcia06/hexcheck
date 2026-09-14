# hexcheck

Verificador y esqueleto del estándar **hexagonal por funcionalidad con FastAPI**
que siguen los servicios personales de Camilo. La guía (la skill
`hexagonal-fastapi`) explica el criterio; `hexcheck` comprueba lo mecánico.

```bash
uv add --dev "hexcheck @ git+https://github.com/CamiloGarcia06/hexcheck@v0.2.0"
uv run hexcheck                   # verifica el servicio actual
uv run hexcheck --format github   # anotaciones en Actions
uv run hexcheck --warn            # informa pero sale con 0 (repos en migración)

uvx --from git+https://github.com/CamiloGarcia06/hexcheck@v0.2.0 hexcheck new tareas
cd tareas && uv sync && uv run hexcheck add tasks && task check
```

Solo biblioteca estándar (lee el código con `ast`, no lo ejecuta). Configuración
en `pyproject.toml`:

```toml
[tool.hexcheck]
src = "src/tareas"        # obligatorio
tests = "tests"           # por defecto
allow = ["src/tareas/legacy.py: H001 # pendiente de migrar"]   # excepciones con motivo
```

## Reglas

| Regla | Comprueba |
| --- | --- |
| H001 | `domain/` solo importa stdlib, `shared.errors`, `shared.types` y su propio dominio |
| H002 | `application/` igual, más su propio `application/` y el `domain/` de otras funcionalidades; nunca `infrastructure` |
| H003 | Ninguna funcionalidad importa `application/` ni `infrastructure/` de otra |
| H004 | `shared/` no importa funcionalidades; solo `main.py` importa `infrastructure` (raíz de composición) |
| H005 | Cada `application/<x>.py` tiene `tests/<feature>/test_<x>.py` que nombra su clase |
| H006 | `HTTPException` solo en `shared/api_errors.py` y `shared/api_auth.py` |
| H007 | `infrastructure/api/` no importa `infrastructure/db/` |
| H008 | `os.environ` / `os.getenv` solo en `shared/config.py` |
| H009 | `sqlalchemy` y `alembic` solo bajo `infrastructure/db/` y `shared/db.py`; `sqlmodel` nunca |
| H010 | Cada funcionalidad tiene `domain/`, `application/`, `infrastructure/` y `tests/<feature>/` |
| W001 | (aviso) `datetime.now()`, `date.today()`, `time.time()` o `random` en el núcleo sin un puerto `Clock` |

Además: `fastapi`, `pydantic`, `sqlalchemy`, `httpx`, `requests`, `sqlite3`,
`subprocess` y `socket` nunca entran en `domain/` ni `application/`.

## Estructura que espera

```
src/<app>/
  <feature>/
    domain/           entities.py · ports.py · errors.py
    application/      un caso de uso por archivo, clase con __call__
    infrastructure/   api/{router,schemas,deps}.py · db/{models,repository}.py
  shared/             config.py · db.py · errors.py · types.py · api_errors.py · api_auth.py
  main.py             build_app(settings, deps): la única raíz de composición
tests/<feature>/      fakes.py · test_<caso_de_uso>.py · test_repository.py · test_api.py
```

Una funcionalidad **de infraestructura pura** (un cliente externo que usan
varias, como `anki` o `model` en claude-fluent) lleva igual sus tres carpetas
—`domain/` con su política y sus errores, `application/` puede quedar vacía— y
se inyecta desde `main.py`: ninguna otra funcionalidad importa su
infraestructura (H003).

Errores de dominio → HTTP (`shared/api_errors.py`, fijado por
`tests/test_api_errors.py`): `Unavailable` 503 · `Upstream` 502 · `NotFound`
404 · `Conflict` 409 · `Invalid` 422 · el resto 400.

## Desarrollo

```bash
uv sync && task check          # ruff, pyright (strict), pytest
uv run python tests/fixtures/generate.py   # regenera los mini-servicios de prueba
```

Un fixture por regla en `tests/fixtures/`: el bueno pasa limpio, cada malo falla
solo con su ID. Versiones con tags `vX.Y.Z` y `CHANGELOG.md`.

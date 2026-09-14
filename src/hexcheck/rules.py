"""Las reglas. Cada una recibe el servicio entero y devuelve hallazgos.

Numeración estable: H001-H010 son errores, W001 es aviso. La tabla de
dependencias que aplican está en la skill `hexagonal-fastapi`.
"""

from __future__ import annotations

import ast
import sys
from collections.abc import Iterable, Iterator

from .model import LAYERS, Finding, Import, Layer, Location, Module, Service

# Paquetes que nunca entran en domain/ ni application/, aunque alguno sea stdlib.
FORBIDDEN_IN_CORE = frozenset(
    {
        "fastapi",
        "starlette",
        "pydantic",
        "pydantic_settings",
        "sqlalchemy",
        "sqlmodel",
        "alembic",
        "httpx",
        "requests",
        "aiohttp",
        "sqlite3",
        "subprocess",
        "socket",
    }
)
# Módulos de shared/ que el núcleo (domain, application) sí puede usar.
CORE_SHARED = frozenset({"errors", "types"})
STDLIB = frozenset(sys.stdlib_module_names)

HTTP_EXCEPTION_ALLOWED = frozenset({("api_errors",), ("api_auth",)})
ENV_ALLOWED = frozenset({("config",)})
CLOCK_CALLS = frozenset({"now", "utcnow", "today", "time", "monotonic", "perf_counter"})


def _top(name: str) -> str:
    return name.split(".", 1)[0]


def _is_external_ok_for_core(imp: Import) -> str | None:
    """None si el import externo vale en el núcleo; si no, el motivo."""
    top = _top(imp.module)
    if top in FORBIDDEN_IN_CORE:
        return f"importa {imp.module}"
    if top not in STDLIB:
        return f"importa {imp.module}, que no es de la biblioteca estándar"
    return None


def _describe(loc: Location) -> str:
    if loc.layer in (Layer.DOMAIN, Layer.APPLICATION, Layer.INFRASTRUCTURE):
        return f"{loc.feature}/{loc.layer.value}"
    return loc.layer.value


# ── H001 / H002: el núcleo solo mira hacia dentro ─────────────────────────────


def _core_internal_problem(mod: Module, target: Location) -> str | None:
    own = mod.where.feature
    layer = mod.where.layer
    if target.layer is Layer.SHARED:
        if target.tail and target.tail[0] in CORE_SHARED:
            return None
        used = ".".join(target.tail) or "*"
        return f"solo puede usar shared.errors y shared.types, no shared.{used}"
    if target.layer is Layer.DOMAIN:
        if layer is Layer.DOMAIN and target.feature != own:
            return f"domain no importa el dominio de otra funcionalidad ({target.feature})"
        return None
    if target.layer is Layer.APPLICATION:
        if layer is Layer.APPLICATION and target.feature == own:
            return None
        if layer is Layer.DOMAIN:
            return "domain no importa application"
        return f"no importa application de otra funcionalidad ({target.feature})"
    if target.layer is Layer.INFRASTRUCTURE:
        return "no importa infrastructure"
    if target.layer is Layer.MAIN:
        return "no importa main"
    return f"no importa {_describe(target)}"


def rule_core_imports(svc: Service) -> Iterator[Finding]:
    for mod in svc.modules:
        layer = mod.where.layer
        if layer not in (Layer.DOMAIN, Layer.APPLICATION):
            continue
        rule = "H001" if layer is Layer.DOMAIN else "H002"
        for imp in mod.imports:
            target = svc.locate_import(imp)
            if target is None:
                reason = _is_external_ok_for_core(imp)
            else:
                reason = _core_internal_problem(mod, target)
            if reason:
                yield Finding(rule, mod.rel, imp.lineno, f"{layer.value} {reason}")


# ── H003 / H007: infrastructure no cruza funcionalidades ni salta capas ─────────


def rule_infrastructure_imports(svc: Service) -> Iterator[Finding]:
    for mod in svc.modules:
        if mod.where.layer is not Layer.INFRASTRUCTURE:
            continue
        own = mod.where.feature
        for imp in mod.imports:
            target = svc.locate_import(imp)
            if (
                target is None
                or target.feature == own
                or target.layer in (Layer.SHARED, Layer.MAIN)
            ):
                if (
                    target is not None
                    and target.feature == own
                    and mod.where.sublayer == "api"
                    and target.layer is Layer.INFRASTRUCTURE
                    and target.sublayer == "db"
                ):
                    yield Finding(
                        "H007",
                        mod.rel,
                        imp.lineno,
                        "infrastructure/api no importa infrastructure/db: "
                        "la API recibe casos de uso",
                    )
                continue
            if target.layer in (Layer.APPLICATION, Layer.INFRASTRUCTURE):
                yield Finding(
                    "H003",
                    mod.rel,
                    imp.lineno,
                    f"{own}/infrastructure no importa {_describe(target)} de otra funcionalidad",
                )
                continue
            if mod.where.sublayer == "api" and target.sublayer == "db":
                yield Finding(
                    "H007", mod.rel, imp.lineno, "infrastructure/api no importa infrastructure/db"
                )


# ── H004: shared/ no conoce funcionalidades; solo main.py compone ──────────────


def rule_shared_and_main(svc: Service) -> Iterator[Finding]:
    for mod in svc.modules:
        if mod.where.layer not in (Layer.SHARED, Layer.OTHER):
            continue
        for imp in mod.imports:
            target = svc.locate_import(imp)
            if target is None or target.feature is None:
                continue
            if mod.where.layer is Layer.SHARED:
                yield Finding(
                    "H004",
                    mod.rel,
                    imp.lineno,
                    f"shared no importa ninguna funcionalidad ({target.feature})",
                )
            elif target.layer is Layer.INFRASTRUCTURE:
                yield Finding(
                    "H004",
                    mod.rel,
                    imp.lineno,
                    f"solo main.py compone: no importes {_describe(target)} desde {mod.rel}",
                )


# ── H005: cada caso de uso tiene su test ───────────────────────────────────────


def rule_use_case_tests(svc: Service) -> Iterator[Finding]:
    for mod in svc.modules:
        if mod.where.layer is not Layer.APPLICATION or mod.where.feature is None:
            continue
        stem = mod.path.stem
        if stem.startswith("_"):
            continue
        test_path = svc.cfg.tests / mod.where.feature / f"test_{stem}.py"
        test_rel = test_path.relative_to(svc.cfg.root).as_posix()
        if not test_path.is_file():
            yield Finding("H005", mod.rel, 1, f"caso de uso sin test: falta {test_rel}")
            continue
        if mod.classes:
            text = test_path.read_text(encoding="utf-8")
            if not any(cls in text for cls in mod.classes):
                yield Finding(
                    "H005",
                    mod.rel,
                    1,
                    f"{test_rel} no nombra ninguna clase de este caso de uso "
                    f"({', '.join(mod.classes)})",
                )


# ── H006: HTTPException solo en el traductor y en la auth ─────────────────────


def _uses_name(tree: ast.Module, name: str) -> Iterator[int]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == name:
            yield node.lineno
        elif isinstance(node, ast.Attribute) and node.attr == name:
            yield node.lineno
        elif isinstance(node, ast.ImportFrom) and any(a.name == name for a in node.names):
            yield node.lineno


def rule_http_exception(svc: Service) -> Iterator[Finding]:
    for mod in svc.modules:
        if mod.where.layer is Layer.SHARED and mod.where.tail in HTTP_EXCEPTION_ALLOWED:
            continue
        seen: set[int] = set()
        for lineno in _uses_name(mod.tree, "HTTPException"):
            if lineno in seen:
                continue
            seen.add(lineno)
            yield Finding(
                "H006",
                mod.rel,
                lineno,
                "HTTPException solo en shared/api_errors.py y shared/api_auth.py: "
                "lanza un error de dominio",
            )


# ── H008: el entorno se lee en un solo sitio ───────────────────────────────────


def _env_uses(tree: ast.Module) -> Iterator[int]:
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "os"
            and node.attr in {"environ", "environb", "getenv", "putenv"}
        ):
            yield node.lineno
        elif (
            isinstance(node, ast.ImportFrom)
            and node.module == "os"
            and any(a.name in {"environ", "environb", "getenv", "putenv"} for a in node.names)
        ):
            yield node.lineno


def rule_environment(svc: Service) -> Iterator[Finding]:
    for mod in svc.modules:
        if mod.where.layer is Layer.SHARED and mod.where.tail in ENV_ALLOWED:
            continue
        seen: set[int] = set()
        for lineno in _env_uses(mod.tree):
            if lineno in seen:
                continue
            seen.add(lineno)
            yield Finding(
                "H008", mod.rel, lineno, "el entorno solo se lee en shared/config.py (Settings)"
            )


# ── H009: el ORM vive en infrastructure/db y shared/db ─────────────────────────


def rule_orm_location(svc: Service) -> Iterator[Finding]:
    for mod in svc.modules:
        where = mod.where
        allowed = (where.layer is Layer.INFRASTRUCTURE and where.sublayer == "db") or (
            where.layer is Layer.SHARED and where.tail == ("db",)
        )
        for imp in mod.imports:
            top = _top(imp.module)
            if top == "sqlmodel":
                yield Finding(
                    "H009", mod.rel, imp.lineno, "sqlmodel no se usa: funde entidad y tabla"
                )
            elif top in {"sqlalchemy", "alembic"} and not allowed:
                yield Finding(
                    "H009",
                    mod.rel,
                    imp.lineno,
                    f"{top} solo bajo infrastructure/db/ y shared/db.py",
                )


# ── H010: estructura completa y espejo en tests ────────────────────────────────


def rule_structure(svc: Service) -> Iterator[Finding]:
    for feature in svc.features:
        base = svc.cfg.src / feature
        rel = base.relative_to(svc.cfg.root).as_posix()
        missing = [layer for layer in LAYERS if not (base / layer).is_dir()]
        if missing:
            yield Finding("H010", rel, 1, f"funcionalidad {feature} sin {', '.join(missing)}/")
        tests_dir = svc.cfg.tests / feature
        if not tests_dir.is_dir():
            tests_rel = tests_dir.relative_to(svc.cfg.root).as_posix()
            yield Finding("H010", rel, 1, f"funcionalidad {feature} sin tests: falta {tests_rel}/")


# ── W001: el tiempo y el azar entran por un puerto ─────────────────────────────


def _features_with_clock(svc: Service) -> frozenset[str]:
    return frozenset(
        m.where.feature
        for m in svc.modules
        if m.where.layer is Layer.DOMAIN and m.where.feature and "Clock" in m.classes
    )


def _clock_or_random_uses(tree: ast.Module) -> Iterator[tuple[int, str]]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in CLOCK_CALLS:
                yield node.lineno, f"{ast.unparse(node.func)}()"
        elif isinstance(node, ast.Import) and any(_top(a.name) == "random" for a in node.names):
            yield node.lineno, "random"
        elif isinstance(node, ast.ImportFrom) and node.module and _top(node.module) == "random":
            yield node.lineno, "random"


def rule_clock(svc: Service) -> Iterator[Finding]:
    with_clock = _features_with_clock(svc)
    for mod in svc.modules:
        if (
            mod.where.layer not in (Layer.DOMAIN, Layer.APPLICATION)
            or mod.where.feature in with_clock
        ):
            continue
        for lineno, what in _clock_or_random_uses(mod.tree):
            yield Finding(
                "W001",
                mod.rel,
                lineno,
                f"{what} en {mod.where.layer.value}: "
                "el tiempo y el azar entran por un puerto Clock",
            )


ALL_RULES = (
    rule_core_imports,
    rule_infrastructure_imports,
    rule_shared_and_main,
    rule_use_case_tests,
    rule_http_exception,
    rule_environment,
    rule_orm_location,
    rule_structure,
    rule_clock,
)


def run_rules(svc: Service, extra: Iterable[Finding] = ()) -> list[Finding]:
    findings = list(extra)
    for rule in ALL_RULES:
        findings.extend(rule(svc))
    findings = [f for f in findings if not svc.cfg.allowed(f.rel, f.rule)]
    return sorted(set(findings), key=lambda f: (f.rel, f.lineno, f.rule))

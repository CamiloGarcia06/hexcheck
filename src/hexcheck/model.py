"""Modelo de un servicio ya clasificado: módulos, capas e imports resueltos."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from .config import Config

LAYERS = ("domain", "application", "infrastructure")


class Layer(StrEnum):
    DOMAIN = "domain"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    SHARED = "shared"
    MAIN = "main"
    OTHER = "other"


@dataclass(frozen=True)
class Location:
    """Dónde cae un módulo (o un módulo importado) dentro del servicio."""

    layer: Layer
    feature: str | None = None
    sublayer: str | None = None  # "api" | "db" | otro, solo en infrastructure
    tail: tuple[str, ...] = ()  # partes después de la capa (p. ej. ("errors",))


@dataclass(frozen=True)
class Import:
    module: str  # nombre absoluto con puntos
    names: tuple[str, ...]  # nombres de `from x import a, b`; vacío en `import x`
    lineno: int


@dataclass
class Module:
    path: Path
    rel: str  # ruta relativa a la raíz del repo, en formato posix
    name: str  # nombre con puntos, p. ej. tareas.tasks.domain.entities
    where: Location
    tree: ast.Module
    imports: list[Import] = field(default_factory=list[Import])
    classes: list[str] = field(default_factory=list[str])


@dataclass(frozen=True)
class Finding:
    rule: str
    rel: str
    lineno: int
    message: str

    @property
    def is_warning(self) -> bool:
        return self.rule.startswith("W")


def locate(parts: tuple[str, ...]) -> Location:
    """Clasifica una ruta relativa al paquete de la app, sin la extensión.

    ("tasks", "domain", "entities") -> domain de tasks
    ("shared", "errors")            -> shared
    ("main",)                       -> main
    """
    if not parts:
        return Location(Layer.OTHER)
    if parts[0] == "shared":
        return Location(Layer.SHARED, tail=parts[1:])
    if parts == ("main",):
        return Location(Layer.MAIN)
    if len(parts) >= 2 and parts[1] in LAYERS:
        layer = Layer(parts[1])
        sublayer = parts[2] if layer is Layer.INFRASTRUCTURE and len(parts) >= 3 else None
        return Location(layer, feature=parts[0], sublayer=sublayer, tail=parts[2:])
    return Location(Layer.OTHER, feature=parts[0] if len(parts) >= 1 else None, tail=parts[1:])


def module_name(cfg: Config, path: Path) -> str:
    rel = path.relative_to(cfg.src.parent).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _resolve_relative(current: str, is_package: bool, level: int, module: str | None) -> str:
    base = current.split(".")
    if not is_package:
        base = base[:-1]
    if level > 1:
        base = base[: len(base) - (level - 1)]
    if module:
        base.extend(module.split("."))
    return ".".join(base)


def collect_imports(mod_name: str, is_package: bool, tree: ast.Module) -> list[Import]:
    found: list[Import] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.append(Import(alias.name, (), node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                target = _resolve_relative(mod_name, is_package, node.level, node.module)
            else:
                target = node.module or ""
            found.append(Import(target, tuple(a.name for a in node.names), node.lineno))
    return found


def load_module(cfg: Config, path: Path) -> Module:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    name = module_name(cfg, path)
    is_package = path.name == "__init__.py"
    app_parts = tuple(name.split(".")[1:])  # sin el nombre de la app
    where = locate(app_parts)
    classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
    return Module(
        path=path,
        rel=path.relative_to(cfg.root).as_posix(),
        name=name,
        where=where,
        tree=tree,
        imports=collect_imports(name, is_package, tree),
        classes=classes,
    )


@dataclass
class Service:
    cfg: Config
    modules: list[Module]
    features: list[str]

    @property
    def known(self) -> frozenset[str]:
        return frozenset(m.name for m in self.modules)

    def locate_import(self, imp: Import) -> Location | None:
        """Ubica un import interno; None si es externo (stdlib o terceros)."""
        prefix = self.cfg.app + "."
        if imp.module != self.cfg.app and not imp.module.startswith(prefix):
            return None
        # `from app.shared import errors` apunta a app.shared.errors si ese módulo existe
        most_specific = imp.module
        for name in imp.names:
            candidate = f"{imp.module}.{name}"
            if candidate in self.known:
                most_specific = candidate
                break
        parts = tuple(most_specific.split(".")[1:])
        return locate(parts)


def discover_features(cfg: Config) -> list[str]:
    features: list[str] = []
    for child in sorted(cfg.src.iterdir()):
        if (
            not child.is_dir()
            or child.name in {"shared", "__pycache__"}
            or child.name.startswith(("_", "."))
        ):
            continue
        if any(p.suffix == ".py" for p in child.rglob("*.py")):
            features.append(child.name)
    return features


def load_service(cfg: Config) -> tuple[Service, list[Finding]]:
    modules: list[Module] = []
    errors: list[Finding] = []
    for path in sorted(cfg.src.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            modules.append(load_module(cfg, path))
        except SyntaxError as exc:  # pragma: no cover - depende del archivo del usuario
            rel = path.relative_to(cfg.root).as_posix()
            errors.append(Finding("E001", rel, exc.lineno or 1, f"no se puede parsear: {exc.msg}"))
    return Service(cfg=cfg, modules=modules, features=discover_features(cfg)), errors

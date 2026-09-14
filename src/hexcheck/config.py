"""Lectura de `[tool.hexcheck]` en pyproject.toml.

Solo tres claves: `src` (obligatoria, p. ej. "src/tareas"), `tests` (por defecto
"tests") y `allow` (excepciones explícitas: "ruta: H001 # motivo").
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast


class ConfigError(Exception):
    """pyproject.toml ausente o sin `[tool.hexcheck]` válido."""


@dataclass(frozen=True)
class Config:
    root: Path
    src: Path
    tests: Path
    allow: dict[str, frozenset[str]] = field(default_factory=dict[str, frozenset[str]])

    @property
    def app(self) -> str:
        return self.src.name

    def allowed(self, rel_path: str, rule: str) -> bool:
        return rule in self.allow.get(rel_path, frozenset())


def find_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").is_file():
            return candidate
    raise ConfigError(f"no encuentro pyproject.toml desde {start}")


def parse_allow(entries: list[str]) -> dict[str, frozenset[str]]:
    allow: dict[str, set[str]] = {}
    for entry in entries:
        body = entry.split("#", 1)[0].strip()
        if ":" not in body:
            raise ConfigError(f"entrada de allow mal formada: {entry!r} (esperaba 'ruta: H001')")
        path, rule = (part.strip() for part in body.split(":", 1))
        if not path or not rule:
            raise ConfigError(f"entrada de allow mal formada: {entry!r}")
        allow.setdefault(path, set()).add(rule)
    return {path: frozenset(rules) for path, rules in allow.items()}


def load_config(start: Path) -> Config:
    root = find_root(start.resolve())
    with (root / "pyproject.toml").open("rb") as fh:
        data: dict[str, Any] = tomllib.load(fh)
    tool = cast(dict[str, Any], data.get("tool", {}))
    raw_section = tool.get("hexcheck")
    if not isinstance(raw_section, dict):
        raise ConfigError("falta [tool.hexcheck] en pyproject.toml")
    section = cast(dict[str, Any], raw_section)
    src_value = section.get("src")
    if not isinstance(src_value, str) or not src_value:
        raise ConfigError('[tool.hexcheck] necesita src = "src/<app>"')
    src = root / src_value
    if not src.is_dir():
        raise ConfigError(f"[tool.hexcheck] src apunta a una carpeta que no existe: {src_value}")
    tests_value = section.get("tests", "tests")
    if not isinstance(tests_value, str):
        raise ConfigError("[tool.hexcheck] tests debe ser una cadena")
    allow_value = section.get("allow", [])
    if not isinstance(allow_value, list):
        raise ConfigError("[tool.hexcheck] allow debe ser una lista de cadenas")
    entries: list[str] = []
    for entry in cast(list[object], allow_value):
        if not isinstance(entry, str):
            raise ConfigError("[tool.hexcheck] allow debe ser una lista de cadenas")
        entries.append(entry)
    return Config(root=root, src=src, tests=root / tests_value, allow=parse_allow(entries))

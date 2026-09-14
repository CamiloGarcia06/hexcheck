"""`hexcheck new` y `hexcheck add`: copian plantillas con marcadores sustituidos.

Las plantillas viven en `templates/service` y `templates/feature`. Los marcadores
(`__APP__`, `__FEATURE__`, `__Entity__`, ...) se sustituyen tanto en el contenido
como en las rutas. `add` además inserta líneas en `main.py` y `tests/conftest.py`
justo antes de los comentarios `# hexcheck:<marcador>`.
"""

from __future__ import annotations

import hashlib
import keyword
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .config import ConfigError, load_config

TEMPLATES = Path(__file__).parent / "templates"
MARKERS = ("imports", "deps", "deps-build", "wire", "fake-imports", "fakes")


class ScaffoldError(Exception):
    pass


def render(text: str, mapping: dict[str, str]) -> str:
    for key in sorted(mapping, key=len, reverse=True):
        text = text.replace(key, mapping[key])
    return text


def copy_tree(source: Path, dest: Path, mapping: dict[str, str]) -> list[Path]:
    written: list[Path] = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        rel = render(path.relative_to(source).as_posix(), mapping)
        target = dest / rel
        if target.exists():
            raise ScaffoldError(f"ya existe {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(path.read_text(encoding="utf-8"), mapping), encoding="utf-8")
        written.append(target)
    return written


def format_files(root: Path, files: list[Path]) -> bool:
    """Formatea con ruff lo generado, si hay un ruff a mano. Best-effort: nunca falla."""
    candidates: list[list[str]] = []
    if shutil.which("ruff"):
        candidates.append(["ruff"])
    if (root / ".venv").is_dir() and shutil.which("uv"):
        candidates.append(["uv", "run", "--no-sync", "ruff"])
    if shutil.which("uvx"):
        candidates.append(["uvx", "ruff"])
    targets = [str(f) for f in files if f.suffix == ".py"]
    if not targets:
        return True
    for cmd in candidates:
        try:
            sort = subprocess.run(
                [*cmd, "check", "--quiet", "--select", "I", "--fix", *targets],
                cwd=root,
                capture_output=True,
                timeout=120,
                check=False,
            )
            fmt = subprocess.run(
                [*cmd, "format", "--quiet", *targets],
                cwd=root,
                capture_output=True,
                timeout=120,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if sort.returncode == 0 and fmt.returncode == 0:
            return True
    return False


def check_identifier(value: str, what: str) -> None:
    if not value.isidentifier() or keyword.iskeyword(value) or value != value.lower():
        raise ScaffoldError(f"{what} debe ser un identificador en minúsculas: {value!r}")


def camel(snake: str) -> str:
    return "".join(part.capitalize() for part in snake.split("_"))


def singular(plural: str) -> str:
    if plural.endswith(("us", "ss", "is")):
        return plural
    if plural.endswith("ies"):
        return plural[:-3] + "y"
    if plural.endswith("ses") or plural.endswith("xes"):
        return plural[:-2]
    if plural.endswith("s"):
        return plural[:-1]
    return plural


def insert_before_marker(path: Path, marker: str, snippet: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    tag = f"# hexcheck:{marker}"
    for i, line in enumerate(lines):
        if line.strip().startswith(tag):
            indent = line[: len(line) - len(line.lstrip())]
            block = [
                indent + s + "\n" if s.strip() else "\n" for s in snippet.rstrip("\n").split("\n")
            ]
            lines[i:i] = block
            path.write_text("".join(lines), encoding="utf-8")
            return
    raise ScaffoldError(f"{path} no tiene el marcador '{tag}'; pega el bloque a mano")


def current_head(versions: Path) -> str | None:
    revisions: dict[str, str | None] = {}
    for path in versions.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        rev = re.search(r'^revision\s*=\s*["\']([^"\']+)["\']', text, re.M)
        down = re.search(r"^down_revision\s*=\s*(.+)$", text, re.M)
        if rev:
            down_value = down.group(1).strip().strip("\"'") if down else "None"
            revisions[rev.group(1)] = None if down_value == "None" else down_value
    parents = {d for d in revisions.values() if d}
    heads = [r for r in revisions if r not in parents]
    if len(heads) > 1:
        raise ScaffoldError(f"migrations/versions tiene varias cabezas: {heads}")
    return heads[0] if heads else None


def new_service(name: str, directory: Path | None) -> int:
    app = name.replace("-", "_")
    try:
        check_identifier(app, "el nombre del servicio")
        dest = (directory or Path.cwd() / name).resolve()
        if dest.exists() and any(dest.iterdir()):
            raise ScaffoldError(f"{dest} existe y no está vacía")
        mapping = {"__APP_UPPER__": app.upper(), "__APP__": app, "__NAME__": name}
        written = copy_tree(TEMPLATES / "service", dest, mapping)
    except ScaffoldError as exc:
        print(f"hexcheck new: {exc}", file=sys.stderr)
        return 1
    formatted = format_files(dest, written)
    print(f"servicio {name} creado en {dest} ({len(written)} archivos)")
    if not formatted:
        print("no encontré ruff: ejecuta `task fmt` tras `uv sync`")
    print("siguiente:")
    print(f"  cd {dest.name} && git init && uv sync")
    print("  hexcheck add <funcionalidad>   # p. ej. tasks")
    print("  task check")
    return 0


def add_feature(feature: str, root: Path) -> int:
    try:
        cfg = load_config(root)
        check_identifier(feature, "la funcionalidad")
        if feature == "shared":
            raise ScaffoldError("'shared' no es una funcionalidad")
        if (cfg.src / feature).exists():
            raise ScaffoldError(f"la funcionalidad {feature} ya existe")
        entity = singular(feature)
        versions = cfg.root / "migrations" / "versions"
        head = current_head(versions) if versions.is_dir() else None
        mapping = {
            "__APP_UPPER__": cfg.app.upper(),
            "__APP__": cfg.app,
            "__FEATURE__": feature,
            "__Feature__": camel(feature),
            "__Entity__": camel(entity),
            "__entity__": entity,
            "__REV__": hashlib.sha1(feature.encode()).hexdigest()[:12],
            "__DOWN_REV__": f'"{head}"' if head else "None",
        }
        written = copy_tree(TEMPLATES / "feature", cfg.root, mapping)
        targets = {
            "imports": cfg.src / "main.py",
            "deps": cfg.src / "main.py",
            "deps-build": cfg.src / "main.py",
            "wire": cfg.src / "main.py",
            "fake-imports": cfg.tests / "conftest.py",
            "fakes": cfg.tests / "conftest.py",
        }
        for marker in MARKERS:
            snippet = render(
                (TEMPLATES / "snippets" / f"{marker}.py").read_text(encoding="utf-8"), mapping
            )
            insert_before_marker(targets[marker], marker, snippet)
    except (ConfigError, ScaffoldError) as exc:
        print(f"hexcheck add: {exc}", file=sys.stderr)
        return 1
    formatted = format_files(cfg.root, [*written, cfg.src / "main.py", cfg.tests / "conftest.py"])
    print(f"funcionalidad {feature} añadida: {len(written)} archivos nuevos,")
    print("main.py y tests/conftest.py cableados")
    if not formatted:
        print("no encontré ruff: ejecuta `task fmt`")
    print("siguiente: task check")
    return 0

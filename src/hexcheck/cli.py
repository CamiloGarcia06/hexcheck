"""Línea de comandos: `hexcheck` (verifica), `hexcheck new`, `hexcheck add`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import ConfigError, load_config
from .model import Finding, load_service
from .rules import run_rules


def format_finding(f: Finding, fmt: str) -> str:
    if fmt == "github":
        kind = "warning" if f.is_warning else "error"
        return f"::{kind} file={f.rel},line={f.lineno},title={f.rule}::{f.message}"
    return f"{f.rel}:{f.lineno}: {f.rule} {f.message}"


def check(root: Path, fmt: str, warn_only: bool) -> int:
    try:
        cfg = load_config(root)
    except ConfigError as exc:
        print(f"hexcheck: {exc}", file=sys.stderr)
        return 2
    svc, parse_errors = load_service(cfg)
    findings = run_rules(svc, parse_errors)
    for f in findings:
        print(format_finding(f, fmt))
    errors = [f for f in findings if not f.is_warning]
    warnings = [f for f in findings if f.is_warning]
    summary = f"hexcheck: {len(errors)} errores, {len(warnings)} avisos"
    summary += f" · {len(svc.modules)} módulos, {len(svc.features)} funcionalidades"
    print(summary, file=sys.stderr)
    if errors and not warn_only:
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hexcheck", description=__doc__)
    parser.add_argument("--version", action="version", version=f"hexcheck {__version__}")
    sub = parser.add_subparsers(dest="command")

    p_check = sub.add_parser("check", help="verifica el servicio (es el comando por defecto)")
    p_check.add_argument("--root", type=Path, default=Path.cwd(), help="carpeta del servicio")
    p_check.add_argument("--format", choices=("text", "github"), default="text")
    p_check.add_argument("--warn", action="store_true", help="informa pero sale con 0")

    p_new = sub.add_parser("new", help="crea el esqueleto de un servicio nuevo")
    p_new.add_argument("name", help="nombre del servicio (kebab o snake, p. ej. tareas)")
    p_new.add_argument(
        "--dir", type=Path, default=None, help="carpeta destino (por defecto ./<name>)"
    )

    p_add = sub.add_parser("add", help="añade una funcionalidad con su hexágono y sus tests")
    p_add.add_argument("feature", help="nombre de la funcionalidad, en plural (p. ej. tasks)")
    p_add.add_argument("--root", type=Path, default=Path.cwd(), help="carpeta del servicio")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0].startswith("-") and args[0] not in ("-h", "--help", "--version"):
        args = ["check", *args]
    ns = build_parser().parse_args(args)
    if ns.command in (None, "check"):
        return check(
            getattr(ns, "root", Path.cwd()),
            getattr(ns, "format", "text"),
            getattr(ns, "warn", False),
        )
    from . import scaffold

    if ns.command == "new":
        return scaffold.new_service(ns.name, ns.dir)
    if ns.command == "add":
        return scaffold.add_feature(ns.feature, ns.root)
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

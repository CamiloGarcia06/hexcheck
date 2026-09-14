"""`hexcheck new` + `hexcheck add` producen un servicio que el propio verificador aprueba."""

from __future__ import annotations

from pathlib import Path

from hexcheck.cli import main
from hexcheck.config import load_config
from hexcheck.model import load_service
from hexcheck.rules import run_rules
from hexcheck.scaffold import camel, current_head, singular


def test_singular_and_camel() -> None:
    assert singular("tasks") == "task"
    assert singular("categories") == "category"
    assert singular("addresses") == "address"
    assert singular("status") == "status"
    assert camel("subscription_renewals") == "SubscriptionRenewals"


def test_new_then_add_twice_passes_hexcheck(tmp_path: Path, monkeypatch: object) -> None:
    dest = tmp_path / "demo"
    assert main(["new", "demo", "--dir", str(dest)]) == 0
    assert (dest / "src" / "demo" / "main.py").is_file()
    assert (dest / "pyproject.toml").is_file()

    assert main(["add", "items", "--root", str(dest)]) == 0
    assert main(["add", "subscription_renewals", "--root", str(dest)]) == 0

    main_py = (dest / "src" / "demo" / "main.py").read_text()
    assert "app.include_router(items_router)" in main_py
    assert "app.include_router(subscription_renewals_router)" in main_py
    assert main_py.count("# hexcheck:wire") == 1
    conftest = (dest / "tests" / "conftest.py").read_text()
    assert '"subscription_renewal_repository": InMemorySubscriptionRenewalRepository()' in conftest

    versions = dest / "migrations" / "versions"
    heads = current_head(versions)
    assert heads is not None
    assert len(list(versions.glob("*.py"))) == 2

    cfg = load_config(dest)
    svc, errors = load_service(cfg)
    assert errors == []
    assert run_rules(svc) == []
    assert svc.features == ["items", "subscription_renewals"]


def test_add_refuses_duplicates_and_shared(tmp_path: Path) -> None:
    dest = tmp_path / "svc"
    assert main(["new", "svc", "--dir", str(dest)]) == 0
    assert main(["add", "items", "--root", str(dest)]) == 0
    assert main(["add", "items", "--root", str(dest)]) == 1
    assert main(["add", "shared", "--root", str(dest)]) == 1
    assert main(["add", "Bad-Name", "--root", str(dest)]) == 1


def test_new_refuses_non_empty_dir(tmp_path: Path) -> None:
    (tmp_path / "x.txt").write_text("")
    assert main(["new", "svc", "--dir", str(tmp_path)]) == 1

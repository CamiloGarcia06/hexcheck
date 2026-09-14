from __future__ import annotations

from pathlib import Path

import pytest

from hexcheck.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_check_exit_codes_and_github_format(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--root", str(FIXTURES / "ok_project")]) == 0
    assert main(["check", "--root", str(FIXTURES / "bad_h001")]) == 1
    assert main(["check", "--root", str(FIXTURES / "bad_h001"), "--warn"]) == 0
    main(["check", "--root", str(FIXTURES / "bad_h001"), "--format", "github"])
    out = capsys.readouterr().out
    assert "::error file=src/app/items/domain/entities.py" in out


def test_missing_config_is_exit_2(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    assert main(["check", "--root", str(tmp_path)]) == 2

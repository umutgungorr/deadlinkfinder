"""End-to-end tests for DeadLinkFinder CLI."""

from pathlib import Path

from deadlinkfinder.main import build_parser, main


def test_cli_help() -> None:
    parser = build_parser()
    assert parser.prog == "deadlinkfinder"


def test_cli_clean_project_exits_zero(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("# Hello World\n[Self Link](#hello-world)\n", encoding="utf-8")

    exit_code = main([str(readme)])
    assert exit_code == 0


def test_cli_broken_project_exits_one(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("# Hello World\n[Broken Link](./missing_subfile.md)\n", encoding="utf-8")

    exit_code = main([str(readme)])
    assert exit_code == 1

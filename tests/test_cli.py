"""End-to-end tests for DeadLinkFinder CLI."""

import json
from pathlib import Path

from deadlinkfinder.main import build_parser, main


def test_cli_help() -> None:
    parser = build_parser()
    assert parser.prog == "deadlinkfinder"


def test_cli_clean_fixture_exits_zero() -> None:
    fixture = Path(__file__).parent / "fixtures" / "valid_doc.md"
    exit_code = main([str(fixture)])
    assert exit_code == 0


def test_cli_broken_fixture_exits_one() -> None:
    fixture = Path(__file__).parent / "fixtures" / "broken_doc.md"
    exit_code = main([str(fixture)])
    assert exit_code == 1


def test_cli_missing_path_exits_two() -> None:
    exit_code = main(["non_existent_folder_abc123/doc.md"])
    assert exit_code == 2


def test_cli_format_json(tmp_path: Path) -> None:
    fixture = Path(__file__).parent / "fixtures" / "broken_doc.md"
    out_file = tmp_path / "report.json"

    exit_code = main(["--format", "json", "-o", str(out_file), str(fixture)])
    assert exit_code == 1
    assert out_file.is_file()

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["clean"] is False
    assert data["broken_count"] == 2
    rule_ids = {b["rule_id"] for b in data["broken_links"]}
    assert "DLF-001" in rule_ids
    assert "DLF-002" in rule_ids


def test_cli_format_sarif(tmp_path: Path) -> None:
    fixture = Path(__file__).parent / "fixtures" / "broken_doc.md"
    out_file = tmp_path / "report.sarif"

    exit_code = main(["--format", "sarif", "-o", str(out_file), str(fixture)])
    assert exit_code == 1
    assert out_file.is_file()

    sarif = json.loads(out_file.read_text(encoding="utf-8"))
    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["tool"]["driver"]["name"] == "DeadLinkFinder"
    assert len(sarif["runs"][0]["results"]) == 2

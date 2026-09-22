"""Tests for link verification and broken link detection."""

from pathlib import Path

from deadlinkfinder.verifier import LinkVerifier, verify_markdown_files


def test_valid_local_links_pass(tmp_path: Path) -> None:
    doc_file = tmp_path / "README.md"
    target_file = tmp_path / "guide.md"

    target_file.write_text("# Guide\n## Setup\nSetup details here.", encoding="utf-8")
    doc_file.write_text(
        "# Main\n[Read Guide](./guide.md)\n[Setup Section](./guide.md#setup)\n[Internal](#main)\n",
        encoding="utf-8",
    )

    report = verify_markdown_files([doc_file], root_dir=tmp_path)
    assert report.is_clean is True
    assert len(report.broken_links) == 0


def test_missing_local_file_detected(tmp_path: Path) -> None:
    doc_file = tmp_path / "README.md"
    doc_file.write_text("[Missing File](./non_existent.md)\n", encoding="utf-8")

    report = verify_markdown_files([doc_file], root_dir=tmp_path)
    assert report.is_clean is False
    assert len(report.broken_links) == 1
    assert "does not exist" in report.broken_links[0].reason


def test_missing_heading_anchor_detected(tmp_path: Path) -> None:
    doc_file = tmp_path / "README.md"
    doc_file.write_text("# Main Title\n\n[Broken Anchor](#non-existent-header)\n", encoding="utf-8")

    report = verify_markdown_files([doc_file], root_dir=tmp_path)
    assert report.is_clean is False
    assert len(report.broken_links) == 1
    assert "Anchor '#non-existent-header' not found" in report.broken_links[0].reason


def test_fuzzy_suggestion_for_typo_in_path(tmp_path: Path) -> None:
    doc_file = tmp_path / "README.md"
    (tmp_path / "documentation.md").write_text("# Docs", encoding="utf-8")

    # Typo: 'documntation.md'
    doc_file.write_text("[Docs](./documntation.md)\n", encoding="utf-8")

    verifier = LinkVerifier(root_dir=tmp_path)
    from deadlinkfinder.extractor import extract_links_from_file

    refs = extract_links_from_file(doc_file)
    broken = verifier.verify_reference(refs[0])

    assert broken is not None
    assert broken.suggestion is not None
    assert "documentation.md" in broken.suggestion

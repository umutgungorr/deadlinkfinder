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


def test_valid_rst_links_pass(tmp_path: Path) -> None:
    doc_file = tmp_path / "index.rst"
    target_file = tmp_path / "guide.rst"

    target_file.write_text(
        "Guide\n=====\n\n.. _setup:\n\nSetup\n-----\nDetails here.\n", encoding="utf-8"
    )
    doc_file.write_text(
        "Main\n====\n\n`Read Guide <./guide.rst>`_\n`Setup Section <./guide.rst#setup>`_\n`Header Anchor <./guide.rst#setup>`_\n",
        encoding="utf-8",
    )

    report = verify_markdown_files([doc_file], root_dir=tmp_path)
    assert report.is_clean is True
    assert len(report.broken_links) == 0


def test_missing_rst_local_file_detected(tmp_path: Path) -> None:
    doc_file = tmp_path / "index.rst"
    doc_file.write_text("`Missing File <./non_existent.rst>`_\n", encoding="utf-8")

    report = verify_markdown_files([doc_file], root_dir=tmp_path)
    assert report.is_clean is False
    assert len(report.broken_links) == 1
    assert "does not exist" in report.broken_links[0].reason


def test_missing_rst_image_detected(tmp_path: Path) -> None:
    doc_file = tmp_path / "index.rst"
    doc_file.write_text(".. image:: ./assets/missing_logo.png\n   :alt: Logo\n", encoding="utf-8")

    report = verify_markdown_files([doc_file], root_dir=tmp_path)
    assert report.is_clean is False
    assert len(report.broken_links) == 1
    assert report.broken_links[0].rule_id == "DLF-004"
    assert report.broken_links[0].reference.is_image is True


def test_missing_rst_heading_anchor_detected(tmp_path: Path) -> None:
    doc_file = tmp_path / "index.rst"
    doc_file.write_text(
        "Main Title\n==========\n\n`Broken Anchor <#non-existent-header>`_\n", encoding="utf-8"
    )

    report = verify_markdown_files([doc_file], root_dir=tmp_path)
    assert report.is_clean is False
    assert len(report.broken_links) == 1
    assert "Anchor '#non-existent-header' not found" in report.broken_links[0].reason

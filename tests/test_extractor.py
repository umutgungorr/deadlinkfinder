"""Tests for Markdown link and image extractor."""

from deadlinkfinder.extractor import extract_links_from_text


def test_extracts_markdown_links() -> None:
    doc = """
Check out the [Documentation](./docs/readme.md) and [License](LICENSE).
Also see [Website](https://example.com).
"""
    refs = extract_links_from_text(doc)
    assert len(refs) == 3

    local_doc = refs[0]
    assert local_doc.display_text == "Documentation"
    assert local_doc.target_path == "./docs/readme.md"
    assert local_doc.is_external is False
    assert local_doc.is_image is False

    license_ref = refs[1]
    assert license_ref.target_path == "LICENSE"
    assert license_ref.is_external is False

    ext_ref = refs[2]
    assert ext_ref.is_external is True


def test_extracts_images() -> None:
    doc = "![Banner](assets/banner.png)\n"
    refs = extract_links_from_text(doc)
    assert len(refs) == 1
    assert refs[0].is_image is True
    assert refs[0].target_path == "assets/banner.png"


def test_extracts_anchor_links() -> None:
    doc = "[Jump to setup](#setup)\n[Cross doc anchor](other.md#section-one)"
    refs = extract_links_from_text(doc)
    assert len(refs) == 2
    assert refs[0].target_path == ""
    assert refs[0].anchor == "setup"

    assert refs[1].target_path == "other.md"
    assert refs[1].anchor == "section-one"


def test_ignores_links_in_code_blocks() -> None:
    doc = """
[Real Link](real.md)

```bash
# Code block:
curl -s http://ignore-me.com/api
[Fake Link](fake.md)
```

And inline code `[Also Fake](ignore.md)` is ignored.
"""
    refs = extract_links_from_text(doc)
    assert len(refs) == 1
    assert refs[0].target_path == "real.md"

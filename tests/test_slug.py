"""Tests for GitHub-compatible heading anchor slug generation."""

from deadlinkfinder.slug import extract_headings_from_markdown, generate_heading_slug


def test_basic_heading_slug() -> None:
    assert generate_heading_slug("Quick Start") == "quick-start"
    assert generate_heading_slug("Installation & Setup") == "installation--setup"
    assert generate_heading_slug("What is TokenGuard?") == "what-is-tokenguard"


def test_strips_formatting_and_emojis() -> None:
    assert generate_heading_slug("🚀 Hızlı Başlangıç") == "hızlı-başlangıç"
    assert generate_heading_slug("Feature: **Zero-Dependency**") == "feature-zero-dependency"
    assert generate_heading_slug("Using `pip install`") == "using-pip-install"


def test_handles_duplicate_headings() -> None:
    doc = """
# Overview
## Features
Some text
## Features
More text
## Features
"""
    anchors = extract_headings_from_markdown(doc)
    assert "overview" in anchors
    assert "features" in anchors
    assert "features-1" in anchors
    assert "features-2" in anchors


def test_ignores_headings_inside_fenced_code_blocks() -> None:
    doc = """
# Real Heading

```markdown
# Fake Heading in Code Block
## Another Fake Heading
```

## Another Real Heading
"""
    anchors = extract_headings_from_markdown(doc)
    assert "real-heading" in anchors
    assert "another-real-heading" in anchors
    assert "fake-heading-in-code-block" not in anchors

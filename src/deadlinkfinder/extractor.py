"""Markdown link and image reference extraction."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class LinkReference:
    raw_target: str
    display_text: str
    source_file: str
    line_number: int
    is_image: bool
    is_external: bool
    target_path: str
    anchor: str | None


EXTERNAL_SCHEMES = ("http://", "https://", "mailto:", "ftp://", "tel:")

# Matches markdown link: optional '!', '[text]', '(url)'
MARKDOWN_LINK_PATTERN = re.compile(r"""(?P<img_flag>!?)\[(?P<text>[^\]]*)\]\((?P<target>[^)]+)\)""")

# Matches HTML href and src attributes: <a href="..."> or <img src="...">
HTML_LINK_PATTERN = re.compile(r"""<(?:a\s+[^>]*href|img\s+[^>]*src)=["']([^"']+)["']""", re.IGNORECASE)


def parse_target_url(raw_target: str) -> tuple[bool, str, str | None]:
    """Parse raw target string into (is_external, path_without_anchor, anchor)."""
    target = raw_target.strip().split(maxsplit=1)[0]  # strip optional title: (url "title")
    target = target.strip("<>")  # handle (<url>) syntax

    for scheme in EXTERNAL_SCHEMES:
        if target.startswith(scheme):
            return True, target, None

    if "#" in target:
        path_part, anchor_part = target.split("#", 1)
        return False, path_part, anchor_part.strip()

    return False, target, None


def extract_links_from_text(content: str, source_file: str = "<stdin>") -> list[LinkReference]:
    """Extract all link and image references from markdown content."""
    references: list[LinkReference] = []
    lines = content.splitlines()
    in_code_block = False

    for idx, line in enumerate(lines, start=1):
        trimmed = line.strip()

        # Toggle fenced code block
        if trimmed.startswith(("```", "~~~")):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Strip inline code spans to avoid checking sample links in code backticks
        clean_line = re.sub(r"`[^`]*`", "", line)

        # 1. Extract Markdown links and images: [text](target) or ![alt](target)
        for match in MARKDOWN_LINK_PATTERN.finditer(clean_line):
            is_image = bool(match.group("img_flag"))
            display_text = match.group("text")
            raw_target = match.group("target")

            is_ext, target_path, anchor = parse_target_url(raw_target)
            references.append(
                LinkReference(
                    raw_target=raw_target,
                    display_text=display_text,
                    source_file=source_file,
                    line_number=idx,
                    is_image=is_image,
                    is_external=is_ext,
                    target_path=target_path,
                    anchor=anchor,
                )
            )

        # 2. Extract HTML link tags: <a href="..."> or <img src="...">
        for match in HTML_LINK_PATTERN.finditer(clean_line):
            raw_target = match.group(1)
            is_ext, target_path, anchor = parse_target_url(raw_target)
            references.append(
                LinkReference(
                    raw_target=raw_target,
                    display_text="<html-tag>",
                    source_file=source_file,
                    line_number=idx,
                    is_image="<img" in match.group(0).lower(),
                    is_external=is_ext,
                    target_path=target_path,
                    anchor=anchor,
                )
            )

    return references


def extract_links_from_file(file_path: Path) -> list[LinkReference]:
    """Extract all link references from a markdown file on disk."""
    if not file_path.is_file():
        return []
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        return extract_links_from_text(content, source_file=str(file_path))
    except OSError:
        return []

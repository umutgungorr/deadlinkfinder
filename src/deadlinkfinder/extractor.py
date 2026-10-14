"""Markdown and reStructuredText link and image reference extraction."""

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
HTML_LINK_PATTERN = re.compile(
    r"""<(?:a\s+[^>]*href|img\s+[^>]*src)=["']([^"']+)["']""", re.IGNORECASE
)

# reStructuredText patterns
RST_INLINE_LINK_PATTERN = re.compile(r"""`(?P<text>[^`\n]+?)\s*<(?P<target>[^>\n]+)>`_{1,2}""")
RST_TARGET_LINK_PATTERN = re.compile(r"""^\s*\.\.\s+_(?P<name>[^:]+):\s+(?P<target>\S+)""")
RST_IMAGE_PATTERN = re.compile(r"""^\s*\.\.\s+(?:image|figure)::\s+(?P<target>\S+)""")
RST_ROLE_PATTERN = re.compile(r""":(?:doc|ref|download):`(?P<content>[^`]+)`""")


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


def extract_links_from_rst(content: str, source_file: str = "<stdin>") -> list[LinkReference]:
    """Extract all link and image references from reStructuredText content."""
    references: list[LinkReference] = []
    lines = content.splitlines()
    in_code_block = False
    code_block_indent = 0
    in_fenced_block = False

    for idx, line in enumerate(lines, start=1):
        trimmed = line.strip()

        # Handle fenced markdown blocks if present
        if trimmed.startswith(("```", "~~~")):
            in_fenced_block = not in_fenced_block
            continue
        if in_fenced_block:
            continue

        # Handle indented literal/code blocks in RST
        if in_code_block:
            if not trimmed:
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent > code_block_indent:
                continue
            in_code_block = False

        if trimmed.startswith((".. code-block::", ".. code::", ".. sourcecode::")) or (
            trimmed.endswith("::") and not trimmed.startswith("..")
        ):
            in_code_block = True
            code_block_indent = len(line) - len(line.lstrip())
            continue

        # Strip double-backtick inline code spans in RST
        clean_line = re.sub(r"``.*?``", "", line)

        # 1. RST image/figure directives: .. image:: path or .. figure:: path
        for match in RST_IMAGE_PATTERN.finditer(clean_line):
            raw_target = match.group("target")
            is_ext, target_path, anchor = parse_target_url(raw_target)
            references.append(
                LinkReference(
                    raw_target=raw_target,
                    display_text=raw_target,
                    source_file=source_file,
                    line_number=idx,
                    is_image=True,
                    is_external=is_ext,
                    target_path=target_path,
                    anchor=anchor,
                )
            )

        # 2. RST explicit target definitions: .. _name: target
        for match in RST_TARGET_LINK_PATTERN.finditer(clean_line):
            raw_target = match.group("target")
            name = match.group("name").strip()
            is_ext, target_path, anchor = parse_target_url(raw_target)
            references.append(
                LinkReference(
                    raw_target=raw_target,
                    display_text=name,
                    source_file=source_file,
                    line_number=idx,
                    is_image=False,
                    is_external=is_ext,
                    target_path=target_path,
                    anchor=anchor,
                )
            )

        # 3. RST inline hyperlinks: `Text <target>`_ or `Text <target>`__
        for match in RST_INLINE_LINK_PATTERN.finditer(clean_line):
            display_text = match.group("text").strip()
            raw_target = match.group("target").strip()
            is_ext, target_path, anchor = parse_target_url(raw_target)
            references.append(
                LinkReference(
                    raw_target=raw_target,
                    display_text=display_text,
                    source_file=source_file,
                    line_number=idx,
                    is_image=False,
                    is_external=is_ext,
                    target_path=target_path,
                    anchor=anchor,
                )
            )

        # 4. RST roles: :doc:`...`, :ref:`...`, :download:`...`
        for match in RST_ROLE_PATTERN.finditer(clean_line):
            role_call = match.group(0)
            content_str = match.group("content").strip()
            if "<" in content_str and content_str.endswith(">"):
                text, target = content_str.split("<", 1)
                display_text = text.strip()
                raw_target = target.rstrip(">").strip()
            else:
                display_text = content_str
                raw_target = content_str

            if role_call.startswith(":ref:"):
                is_ext = False
                target_path = ""
                anchor = raw_target
            else:
                is_ext, target_path, anchor = parse_target_url(raw_target)

            references.append(
                LinkReference(
                    raw_target=raw_target,
                    display_text=display_text,
                    source_file=source_file,
                    line_number=idx,
                    is_image=False,
                    is_external=is_ext,
                    target_path=target_path,
                    anchor=anchor,
                )
            )

        # 5. HTML link tags if embedded in RST
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


def extract_links_from_text(content: str, source_file: str = "<stdin>") -> list[LinkReference]:
    """Extract all link and image references from markdown or reStructuredText content."""
    if source_file.lower().endswith(".rst"):
        return extract_links_from_rst(content, source_file=source_file)

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

        # Strip double backtick literals first so sample RST links inside literals are ignored
        line_no_literals = re.sub(r"``.*?``", "", line)

        # Extract any RST links on the line before stripping single backticks
        for match in RST_INLINE_LINK_PATTERN.finditer(line_no_literals):
            display_text = match.group("text").strip()
            raw_target = match.group("target").strip()
            is_ext, target_path, anchor = parse_target_url(raw_target)
            references.append(
                LinkReference(
                    raw_target=raw_target,
                    display_text=display_text,
                    source_file=source_file,
                    line_number=idx,
                    is_image=False,
                    is_external=is_ext,
                    target_path=target_path,
                    anchor=anchor,
                )
            )

        # RST image or target directives on markdown line
        for match in RST_IMAGE_PATTERN.finditer(line):
            raw_target = match.group("target")
            is_ext, target_path, anchor = parse_target_url(raw_target)
            references.append(
                LinkReference(
                    raw_target=raw_target,
                    display_text=raw_target,
                    source_file=source_file,
                    line_number=idx,
                    is_image=True,
                    is_external=is_ext,
                    target_path=target_path,
                    anchor=anchor,
                )
            )

        for match in RST_TARGET_LINK_PATTERN.finditer(line):
            raw_target = match.group("target")
            name = match.group("name").strip()
            is_ext, target_path, anchor = parse_target_url(raw_target)
            references.append(
                LinkReference(
                    raw_target=raw_target,
                    display_text=name,
                    source_file=source_file,
                    line_number=idx,
                    is_image=False,
                    is_external=is_ext,
                    target_path=target_path,
                    anchor=anchor,
                )
            )

        for match in RST_ROLE_PATTERN.finditer(line):
            role_call = match.group(0)
            content_str = match.group("content").strip()
            if "<" in content_str and content_str.endswith(">"):
                text, target = content_str.split("<", 1)
                display_text = text.strip()
                raw_target = target.rstrip(">").strip()
            else:
                display_text = content_str
                raw_target = content_str

            if role_call.startswith(":ref:"):
                is_ext = False
                target_path = ""
                anchor = raw_target
            else:
                is_ext, target_path, anchor = parse_target_url(raw_target)

            references.append(
                LinkReference(
                    raw_target=raw_target,
                    display_text=display_text,
                    source_file=source_file,
                    line_number=idx,
                    is_image=False,
                    is_external=is_ext,
                    target_path=target_path,
                    anchor=anchor,
                )
            )

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
    """Extract all link references from a markdown or reStructuredText file on disk."""
    if not file_path.is_file():
        return []
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        if file_path.suffix.lower() == ".rst":
            return extract_links_from_rst(content, source_file=str(file_path))
        return extract_links_from_text(content, source_file=str(file_path))
    except OSError:
        return []

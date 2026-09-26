"""GitHub-compatible Markdown heading slug generation."""

from __future__ import annotations

import re


def generate_heading_slug(heading_text: str) -> str:
    """Convert raw Markdown heading text into a GitHub-compatible anchor slug."""
    # 1. Strip HTML tags
    cleaned = re.sub(r"<[^>]+>", "", heading_text)

    # 2. Strip inline markdown formatting (bold, italic, strikethrough, inline code)
    cleaned = re.sub(r"(\*\*|__|\*|_|~~|`)(.*?)\1", r"\2", cleaned)

    # 3. Strip markdown links [text](url) -> text
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)

    # 4. Lowercase
    cleaned = cleaned.lower()

    # 5. Filter: retain alphanumeric characters, hyphens/underscores, convert spaces to hyphens
    # Emojis and punctuation like ?, !, :, (, ), ., ,, ;, @, etc. are stripped
    filtered_chars: list[str] = []
    for char in cleaned:
        if char.isalnum() or char in {"-", "_"}:
            filtered_chars.append(char)
        elif char.isspace():
            filtered_chars.append("-")

    slug = "".join(filtered_chars).strip("-")
    return slug


class HeadingTracker:
    """Track headings within a Markdown document to handle duplicate slugs (-1, -2)."""

    def __init__(self) -> None:
        self._counts: dict[str, int] = {}
        self._anchors: set[str] = set()

    def add_heading(self, heading_text: str) -> str:
        base_slug = generate_heading_slug(heading_text)
        if not base_slug:
            return ""

        count = self._counts.get(base_slug, 0)
        self._counts[base_slug] = count + 1

        final_slug = base_slug if count == 0 else f"{base_slug}-{count}"
        self._anchors.add(final_slug)
        return final_slug

    @property
    def anchors(self) -> set[str]:
        return set(self._anchors)


def extract_headings_from_markdown(content: str) -> set[str]:
    """Scan markdown content for ATX headers (# Header) and return all valid anchor slugs."""
    tracker = HeadingTracker()
    in_code_block = False

    for line in content.splitlines():
        trimmed = line.strip()

        # Handle fenced code blocks
        if trimmed.startswith(("```", "~~~")):
            in_code_block = not in_code_block
            continue

        if in_code_block or not trimmed:
            continue

        # Match ATX headings: # Heading, ## Heading, etc.
        match = re.match(r"^#{1,6}\s+(.+)$", trimmed)
        if match:
            heading_text = match.group(1).strip()
            # Remove trailing closing hashes if present: ## Title ##
            heading_text = re.sub(r"\s+#+$", "", heading_text)
            tracker.add_heading(heading_text)

    return tracker.anchors


def extract_headings_from_rst(content: str) -> set[str]:
    """Scan reStructuredText content for explicit targets and section titles."""
    tracker = HeadingTracker()
    anchors: set[str] = set()
    lines = content.splitlines()
    punct_chars = set("=-~^\"'*+#<>_")
    in_code_block = False
    code_block_indent = 0

    for i, line in enumerate(lines):
        trimmed = line.strip()

        # Handle indented code blocks
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

        if not trimmed:
            continue

        # 1. Explicit target: .. _target-name:
        match_target = re.match(r"^\.\.\s+_([^:]+):\s*$", trimmed)
        if match_target:
            target_name = match_target.group(1).strip()
            anchors.add(target_name)
            anchors.add(generate_heading_slug(target_name))
            continue

        # 2. Section title with underline
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            # Underline must be at least as long as text and consist of single punctuation character
            if (
                next_line
                and len(next_line) >= len(trimmed)
                and len(set(next_line)) == 1
                and next_line[0] in punct_chars
                and not (len(set(trimmed)) == 1 and trimmed[0] in punct_chars)
            ):
                slug = tracker.add_heading(trimmed)
                anchors.add(slug)

    return anchors | tracker.anchors

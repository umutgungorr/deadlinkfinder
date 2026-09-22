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

"""Verification engine for local links, relative paths, and heading anchors."""

from __future__ import annotations

import difflib
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

from .extractor import LinkReference, extract_links_from_file
from .slug import extract_headings_from_markdown


@dataclass(slots=True)
class BrokenLink:
    reference: LinkReference
    reason: str
    suggestion: str | None = None


@dataclass(slots=True)
class VerificationReport:
    total_files_scanned: int
    total_links_found: int
    total_links_checked: int
    broken_links: list[BrokenLink]

    @property
    def is_clean(self) -> bool:
        return len(self.broken_links) == 0


class LinkVerifier:
    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = root_dir or Path.cwd()
        self._heading_cache: dict[Path, set[str]] = {}
        self._all_project_files: list[str] | None = None

    def _get_headings_for_file(self, file_path: Path) -> set[str]:
        resolved = file_path.resolve()
        if resolved in self._heading_cache:
            return self._heading_cache[resolved]

        if not resolved.is_file():
            return set()

        try:
            content = resolved.read_text(encoding="utf-8", errors="replace")
            headings = extract_headings_from_markdown(content)
            self._heading_cache[resolved] = headings
            return headings
        except OSError:
            return set()

    def _get_project_file_list(self) -> list[str]:
        if self._all_project_files is not None:
            return self._all_project_files

        file_list: list[str] = []
        ignored = {".git", ".venv", "venv", "node_modules", "__pycache__"}
        for p in self.root_dir.rglob("*"):
            if any(part in ignored for part in p.parts):
                continue
            if p.is_file():
                try:
                    rel = p.relative_to(self.root_dir).as_posix()
                    file_list.append(rel)
                except ValueError:
                    continue
        self._all_project_files = file_list
        return file_list

    def suggest_similar_path(self, broken_path: str) -> str | None:
        candidates = self._get_project_file_list()
        matches = difflib.get_close_matches(broken_path, candidates, n=1, cutoff=0.5)
        if matches:
            return matches[0]

        # Also check matching by basename
        target_name = Path(broken_path).name.lower()
        for cand in candidates:
            if Path(cand).name.lower() == target_name:
                return cand
        return None

    def verify_reference(self, ref: LinkReference) -> BrokenLink | None:
        # Ignore external HTTP/HTTPS links
        if ref.is_external:
            return None

        # Clean encoded characters (e.g. %20 -> space)
        target_path_raw = unquote(ref.target_path)
        source_path = Path(ref.source_file).resolve()
        source_dir = source_path.parent

        # 1. Pure anchor link on the same file: [Jump](#section)
        if not target_path_raw and ref.anchor:
            headings = self._get_headings_for_file(source_path)
            if ref.anchor not in headings:
                return BrokenLink(
                    reference=ref,
                    reason=f"Anchor '#{ref.anchor}' not found in current file",
                )
            return None

        # 2. File link (e.g. ./docs/guide.md or ../assets/img.png)
        target_file = (source_dir / target_path_raw).resolve()
        if not target_file.exists():
            suggestion = self.suggest_similar_path(target_path_raw)
            return BrokenLink(
                reference=ref,
                reason=f"Target file does not exist: '{ref.target_path}'",
                suggestion=suggestion,
            )

        # 3. File link with anchor (e.g. ./docs/guide.md#installation)
        if ref.anchor and target_file.is_file() and target_file.suffix.lower() == ".md":
            headings = self._get_headings_for_file(target_file)
            if ref.anchor not in headings:
                return BrokenLink(
                    reference=ref,
                    reason=f"File exists, but anchor '#{ref.anchor}' was not found in '{target_file.name}'",
                )

        return None


def verify_markdown_files(
    markdown_files: Iterable[Path],
    root_dir: Path | None = None,
    ignore_external: bool = True,
) -> VerificationReport:
    """Verify all links across provided Markdown files."""
    verifier = LinkVerifier(root_dir=root_dir)
    files_list = list(markdown_files)

    total_links_found = 0
    total_links_checked = 0
    broken_links: list[BrokenLink] = []

    for file_path in files_list:
        refs = extract_links_from_file(file_path)
        total_links_found += len(refs)

        for ref in refs:
            if ignore_external and ref.is_external:
                continue
            total_links_checked += 1
            broken = verifier.verify_reference(ref)
            if broken:
                broken_links.append(broken)

    return VerificationReport(
        total_files_scanned=len(files_list),
        total_links_found=total_links_found,
        total_links_checked=total_links_checked,
        broken_links=broken_links,
    )


def format_verification_report(report: VerificationReport) -> str:
    """Format verification report into a clean, structured CLI message."""
    lines: list[str] = [
        "=" * 68,
        "🔗 DeadLinkFinder Verification Report",
        "=" * 68,
        f"  Files Scanned:   {report.total_files_scanned} markdown file(s)",
        f"  Links Checked:   {report.total_links_checked} of {report.total_links_found} link(s)",
        "-" * 68,
    ]

    if report.is_clean:
        lines.append("✓ PERFECT! All local links, images, and heading anchors are intact.")
    else:
        lines.append(f"[!] FAILED: Found {len(report.broken_links)} broken link(s):\n")
        for b in report.broken_links:
            ref = b.reference
            lines.append(f"  ✗ {ref.source_file}:{ref.line_number}")
            lines.append(f"    Target:     '{ref.raw_target}'")
            lines.append(f"    Reason:     {b.reason}")
            if b.suggestion:
                lines.append(f"    Suggestion: Did you mean '{b.suggestion}'?")
            lines.append("")

    lines.append("=" * 68)
    return "\n".join(lines)

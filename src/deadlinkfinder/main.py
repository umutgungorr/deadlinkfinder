"""Main CLI entrypoint for DeadLinkFinder."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from .verifier import format_verification_report, verify_markdown_files

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deadlinkfinder",
        description="DeadLinkFinder: Fast, zero-dependency Markdown link, image, and heading anchor verifier.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Markdown files or directories to scan (default: current directory)",
    )
    parser.add_argument(
        "--include-external",
        action="store_true",
        help="Include external URLs in link check (default: local and anchor links only)",
    )
    return parser


def find_markdown_files(paths: Sequence[str]) -> list[Path]:
    """Find all markdown files under specified file or directory paths."""
    found: list[Path] = []
    for p_str in paths:
        p = Path(p_str)
        if p.is_file() and p.suffix.lower() in {".md", ".markdown"}:
            found.append(p)
        elif p.is_dir():
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
                for file in files:
                    if file.lower().endswith((".md", ".markdown")):
                        found.append(Path(root) / file)
    return sorted(found)


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code if exc.code is not None else 0)

    md_files = find_markdown_files(args.paths)
    if not md_files:
        print("[!] No Markdown files found in the specified path(s).")
        return 0

    report = verify_markdown_files(
        md_files,
        root_dir=Path.cwd(),
        ignore_external=not args.include_external,
    )

    print(format_verification_report(report))
    return 0 if report.is_clean else 1

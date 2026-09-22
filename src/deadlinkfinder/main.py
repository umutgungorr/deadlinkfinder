"""Main CLI entrypoint for DeadLinkFinder."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from .sarif import to_sarif_json
from .verifier import (
    format_verification_json,
    format_verification_report,
    verify_markdown_files,
)

VERSION = "0.2.0"

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
        description="DeadLinkFinder: Zero-dependency Markdown link, image, and heading anchor verifier with SARIF support.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "sarif"],
        default="text",
        help="Report format: text (human readable), json (machine parseable), sarif (GitHub Code Scanning)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write report output to specified file path instead of stdout",
    )
    parser.add_argument(
        "--check-external",
        action="store_true",
        help="Check external HTTP/HTTPS links over network (default: local and anchor links only)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Force offline mode: skip all external HTTP/HTTPS requests (default)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="HTTP request timeout in seconds for external URLs (default: 5.0)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color codes in console output",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Quiet mode: suppress scan headers and only print detected errors",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose diagnostic output",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Markdown files or directories to scan (default: current directory)",
    )
    return parser


def find_markdown_files(paths: Sequence[str]) -> list[Path]:
    """Find all markdown files under specified file or directory paths."""
    found: list[Path] = []
    for p_str in paths:
        p = Path(p_str)
        if not p.exists():
            continue
        if p.is_file() and p.suffix.lower() in {".md", ".markdown"}:
            found.append(p)
        elif p.is_dir():
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
                for file in files:
                    if file.lower().endswith((".md", ".markdown")):
                        found.append(Path(root) / file)
    return sorted(found)


def _output(content: str, output_path: Path | None = None) -> None:
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content + "\n", encoding="utf-8")
    else:
        print(content)


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
        return 0 if exc.code == 0 else 2

    # Validate that requested paths exist
    for p_str in args.paths:
        p = Path(p_str)
        if not p.exists():
            print(f"Error: Target path does not exist: {p_str}", file=sys.stderr)
            return 2

    md_files = find_markdown_files(args.paths)
    if not md_files:
        if not args.quiet and args.format == "text":
            print("[!] No Markdown files found in the specified path(s).")
        return 0

    use_no_color = args.no_color or ("NO_COLOR" in os.environ)
    check_ext = args.check_external and not args.offline

    report = verify_markdown_files(
        md_files,
        root_dir=Path.cwd(),
        check_external=check_ext,
        http_timeout=args.timeout,
    )

    if args.format == "sarif":
        _output(to_sarif_json(report), args.output)
    elif args.format == "json":
        _output(format_verification_json(report), args.output)
    else:  # text
        _output(format_verification_report(report, no_color=use_no_color), args.output)

    return 0 if report.is_clean else 1


if __name__ == "__main__":
    sys.exit(main())

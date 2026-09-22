# DeadLinkFinder 🔗🔍

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![SARIF v2.1.0](https://img.shields.io/badge/SARIF-v2.1.0-blue?logo=github)](https://docs.github.com/en/code-security/code-scanning)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-20%20passed-brightgreen.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero%20external-success.svg)]()

> **Fast, zero-dependency Markdown link, image, and heading anchor verifier CLI with native SARIF output.**  
> Prevent broken links, missing image assets, and dead `#anchor` fragments in your documentation before they hit production.

---

## 💥 The Problem

Documentation is the front door of your project. Yet, as repositories evolve:
1. **Renamed or Moved Files**: Renaming `docs/setup.md` breaks every incoming link across your repository with silent 404 errors.
2. **Broken Heading Anchors**: Updating `## 🚀 Quick Start` breaks links like `[Quick Start](#quick-start)` because the anchor slug changed or was removed.
3. **Missing Image Assets**: Broken screenshots (`![Architecture](./assets/arch.png)`) leave ugly empty boxes in READMEs.

**DeadLinkFinder** recursively audits your Markdown files in milliseconds with **zero external dependencies**.

---

## 🌟 Key Features

- **Zero External Dependencies**: Pure Python standard library (`re`, `pathlib`, `argparse`, `difflib`, `json`, `urllib`). Runs anywhere without package installation.
- **Native SARIF v2.1.0**: Generates standard OASIS SARIF reports directly consumable by GitHub Code Scanning Alerts and CI dashboards.
- **GitHub-Compatible Anchor Engine**: Perfectly replicates GitHub's GFM heading-to-slug algorithm, handling emojis, accents, punctuation, and duplicate headings (`#section`, `#section-1`).
- **Cross-File Anchor Verification**: Validates links like `[Docs](docs/api.md#endpoints)` by inspecting the target file's headers.
- **Smart Code Block Isolation**: Automatically ignores code blocks (` ```...``` `) and inline backticks so sample URLs in tutorials don't trigger false alarms.
- **Fuzzy "Did You Mean?" Suggestions**: When a local file path is broken due to a typo or move, DeadLinkFinder suggests the closest matching file in your repo.
- **Deterministic Exit Codes**: `0` (clean), `1` (broken links), `2` (CLI / path error).

---

## 🔍 Validation Rules

| Rule ID | Name | Default Level | Description |
|---------|------|---------------|-------------|
| `DLF-001` | Broken Local File Link | `error` | Target local file or image asset does not exist on disk |
| `DLF-002` | Missing Anchor Slug | `warning` | Target `#heading-anchor` not found in target Markdown document |
| `DLF-003` | Broken External URL | `warning` | Remote HTTP/HTTPS URL returned $\ge 400$ or timed out |

---

## 🚀 Quick Start

### 1. Installation

Install via pip:

```bash
pip install .
```

Or run directly without installation:

```bash
python -m deadlinkfinder --help
```

---

## 🛠️ Usage & Examples

### 1. Scan Current Repository (Offline Local Mode)

Recursively scan all Markdown files in the current folder:

```bash
deadlinkfinder
```

### 2. Export SARIF for GitHub Code Scanning

Generate a standard SARIF v2.1.0 report:

```bash
deadlinkfinder --format sarif -o results.sarif
```

### 3. Machine-Parseable JSON Output

```bash
deadlinkfinder --format json -o deadlinks.json
```

### 4. Check External URLs (Optional Network Mode)

```bash
deadlinkfinder --check-external --timeout 5.0
```

---

## ⚙️ CLI Options & Deterministic Exit Codes

```text
usage: deadlinkfinder [-h] [--version] [--format {text,json,sarif}]
                      [-o OUTPUT] [--check-external] [--offline]
                      [--timeout TIMEOUT] [--no-color] [-q] [-v]
                      [paths ...]
```

| Exit Code | Meaning |
|-----------|---------|
| `0` | Success: All local links and anchors are valid |
| `1` | Discrepancy detected: Broken files, missing anchors, or broken URLs |
| `2` | Error: Target path not found or invalid CLI arguments |

---

## 🤖 CI/CD Integration (GitHub Actions)

Catch broken links automatically on every pull request and publish results to GitHub Code Scanning:

```yaml
name: Documentation Integrity

on: [push, pull_request]

jobs:
  deadlinkfinder:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Verify Markdown Links (SARIF)
        run: |
          python -m deadlinkfinder --format sarif -o results.sarif .
        continue-on-error: true
      - name: Upload SARIF to GitHub Code Scanning
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

---

## 🧪 Running Tests

```bash
uv run --with pytest pytest
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

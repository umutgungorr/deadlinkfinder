# DeadLinkFinder 🔗🔍

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-17%20passed-brightgreen.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero%20external-success.svg)]()

> **Fast, zero-dependency Markdown link, image, and heading anchor verifier CLI.**  
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

- **Zero External Dependencies**: Pure Python standard library (`re`, `pathlib`, `argparse`, `difflib`). Runs anywhere without package installation.
- **GitHub-Compatible Anchor Engine**: Perfectly replicates GitHub's GFM heading-to-slug algorithm, handling emojis, accents, punctuation, and duplicate headings (`#section`, `#section-1`).
- **Cross-File Anchor Verification**: Validates links like `[Docs](docs/api.md#endpoints)` by inspecting the target file's headers.
- **Smart Code Block Isolation**: Automatically ignores code blocks (` ```...``` `) and inline backticks so sample URLs in tutorials don't trigger false alarms.
- **Fuzzy "Did You Mean?" Suggestions**: When a local file path is broken due to a typo or move, DeadLinkFinder suggests the closest matching file in your repo.
- **CI/CD Ready**: Exits with code `1` when broken references are found to keep your main branch spotless.

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

### 1. Scan Current Repository

Recursively scan all Markdown files in the current folder:

```bash
deadlinkfinder
```

### 2. Scan Specific Files or Directories

```bash
# Scan a specific file
deadlinkfinder README.md

# Scan documentation folder
deadlinkfinder ./docs
```

**Sample Output:**
```text
====================================================================
🔗 DeadLinkFinder Verification Report
====================================================================
  Files Scanned:   8 markdown file(s)
  Links Checked:   47 of 62 link(s)
--------------------------------------------------------------------
[!] FAILED: Found 2 broken link(s):

  ✗ README.md:42
    Target:     './docs/instalation.md'
    Reason:     Target file does not exist: './docs/instalation.md'
    Suggestion: Did you mean 'docs/installation.md'?

  ✗ docs/api.md:18
    Target:     '#auth-tokens'
    Reason:     Anchor '#auth-tokens' not found in current file

====================================================================
```

---

## 🤖 CI/CD Integration (GitHub Actions)

Catch broken links automatically on every pull request:

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
      - name: Verify Markdown Links
        run: |
          python -m deadlinkfinder .
```

---

## 🧪 Running Tests

```bash
pytest tests contract_tests -v
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

# DeadLinkFinder 🔗🔍

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![SARIF v2.1.0](https://img.shields.io/badge/SARIF-v2.1.0-blue?logo=github)](https://docs.github.com/en/code-security/code-scanning)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-21%20passed-brightgreen.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero%20external-success.svg)]()

> **DeadLinkFinder is a zero-dependency Markdown integrity checker for local links, images, heading anchors, and optional external URLs.**  
> Prevent broken links, missing image assets, and dead `#anchor` fragments in your documentation before they reach production.

<p align="center">
  <img src="assets/demo.png" alt="DeadLinkFinder Demo" width="850">
</p>

```text
$ deadlinkfinder docs/

🔗 DeadLinkFinder v0.2.1 — Verifying documentation integrity...
[!] DLF-001  ERROR    docs/getting-started.md:28
    Target not found: '../guides/setup.md'
    Suggestion: Did you mean '../guides/installation.md'?

[!] DLF-002  WARNING  docs/api-reference.md:104
    Heading anchor not found: '#authentication-keys'

[✗] 2 issues detected across 14 scanned files (exit 1).
    Emitted SARIF report to 'deadlinks.sarif' (OASIS v2.1.0 compliant).
```

---

## 🌟 Architecture & Capabilities

### Core Engine (100% Offline, Zero Network)
- **Zero External Dependencies**: Built strictly using the Python Standard Library (`re`, `pathlib`, `argparse`, `difflib`, `json`, `urllib`). Requires no third-party package installation (`dependencies = []`).
- **GitHub-style Anchor Engine**: Generates GitHub-compatible heading anchors for common GFM Markdown headings, including punctuation, Unicode text, emojis, and duplicate headings (`#section`, `#section-1`). The anchor behavior is covered by compatibility fixtures for common GitHub Markdown cases.
- **Local Asset Verification**: Distinguishes between document pages and image assets (`.png`, `.jpg`, `.svg`), reporting missing assets with dedicated rule IDs.
- **Cross-File Anchor Verification**: Validates complex references like `[API Reference](docs/api.md#authentication)` by inspecting the target file's heading tree.
- **Code Block Isolation**: Automatically ignores fenced code blocks (` ```...``` `) and inline backtick spans so tutorial examples never trigger false alarms.
- **Fuzzy "Did You Mean?" Suggestions**: Suggests closest matching file paths when a relative link has a typo or moved location.
- **Deterministic Exit Codes**: `0` (clean), `1` (broken references found), `2` (CLI error or target not found).

### Optional Network Mode
- **External URL Validation**: When explicitly enabled via `--check-external`, validates remote `http://` and `https://` links.
- **Timeout Management**: Configurable network timeout thresholds (`--timeout 5.0`) with isolated timeout error reporting (`DLF-007`).
- **Offline By Default**: Fast, safe local execution by default without unexpected network calls.

---

## 🔍 Validation Rules

Rule IDs are permanent and deterministic for stable CI/CD and SARIF triage:

| Rule ID | Name | Default Level | Description |
|---------|------|:-------------:|-------------|
| `DLF-001` | Broken Local File Link | `error` | Referenced relative file path does not exist on disk |
| `DLF-002` | Missing Anchor Slug | `warning` | Target `#heading-anchor` not found in target Markdown document |
| `DLF-003` | Broken External URL | `warning` | Remote HTTP/HTTPS URL returned an error status ($\ge 400$) |
| `DLF-004` | Missing Local Image | `error` | Referenced graphic or screenshot asset does not exist on disk |
| `DLF-005` | Invalid Markdown Target | `error` | Target destination is empty or contains malformed syntax |
| `DLF-006` | Skipped Code Block Reference | `note` | Informational rule indicating ignored code snippet URLs |
| `DLF-007` | External URL Timeout | `warning` | Remote URL did not respond within configured timeout |

---

## 🚀 Quick Start

### Installation

Recommended via **pipx** for isolated CLI usage:

```bash
pipx install deadlinkfinder
```

Or install via **pip**:

```bash
pip install .
```

Or run directly from source without installation:

```bash
git clone https://github.com/umutgungorr/deadlinkfinder.git
cd deadlinkfinder
python -m deadlinkfinder .
```

---

## 🛠️ Usage & Examples

### 1. Scan Local Documentation (Core Offline Mode)

Scans local Markdown files quickly with no runtime dependencies. On standard documentation repositories, local scans typically complete in milliseconds:

```bash
deadlinkfinder
```

### 2. Export SARIF for GitHub Code Scanning

SARIF findings include stable partial fingerprints (`partialFingerprints.primaryLocationLineHash`) to prevent duplicate Code Scanning alerts across repeated workflow runs:

```bash
deadlinkfinder --format sarif -o results.sarif
```

### 3. Machine-Parseable JSON Output

```bash
deadlinkfinder --format json -o deadlinks.json
```

### 4. Optional External URL Checking

```bash
deadlinkfinder --check-external --timeout 5.0
```

---

## 🤖 CI/CD Integration (GitHub Actions)

### Option A: PR-Blocking Mode (Fails build on broken links)

Use this when documentation errors should prevent pull requests from merging:

```yaml
name: Documentation Integrity

on: [push, pull_request]

permissions:
  contents: read
  security-events: write

jobs:
  deadlinkfinder:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Verify Documentation Links
        run: |
          python -m deadlinkfinder --format sarif -o results.sarif .

      - name: Upload SARIF to GitHub Code Scanning
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: results.sarif
```

### Option B: Advisory / Reporting-Only Mode

Use `continue-on-error: true` if you only want alerts reported in the GitHub Security tab without blocking PR merges:

```yaml
      - name: Verify Documentation Links (Advisory)
        run: |
          python -m deadlinkfinder --format sarif -o results.sarif .
        continue-on-error: true
```

> **Note**: Remove `continue-on-error: true` if broken documentation should fail the workflow.

---

## 📋 Scope & Known Limitations

### Supported
- Standard Markdown links: `[Text](path/to/doc.md)`
- Relative file references across directories: `../guide.md`
- Relative image links: `![Alt Text](./assets/diagram.png)`
- Same-file heading anchors: `[Jump](#quick-start)`
- Cross-file heading anchors: `[Guide](docs/setup.md#installation)`
- ATX headings with custom punctuation, emojis, and duplicate suffixes (`-1`, `-2`)
- Fenced code block isolation (` ```...``` ` and ` ~~~...~~~ `)
- Inline backtick span isolation (` `...` `)

### Known Limitations
- Complex inline raw HTML tags (`<a href="...">`) receive best-effort regex parsing.
- Reference-style links (`[text][ref]`) with distant definitions have limited support.
- JavaScript-rendered client-side Single Page Application (SPA) links are not executed.
- External URL checks require network access and are skipped by default.

---

## 🧪 Test Coverage

DeadLinkFinder is verified against a comprehensive fixture suite:
- Unicode and multi-language heading slugs
- Emoji-prefixed headings (`## 🚀 Quick Start` $\rightarrow$ `#quick-start`)
- Duplicate heading counters (`#section`, `#section-1`)
- Missing image asset detection (`DLF-004`)
- Cross-file anchor resolution
- Mixed POSIX and Windows backslash paths
- Empty and malformed Markdown targets (`DLF-005`)
- SARIF v2.1.0 schema validity and partial fingerprints

Run tests locally:
```bash
python -m pytest tests contract_tests -v
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

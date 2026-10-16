# 🚀 DeadLinkFinder Launch & Distribution Kit

> **Goal**: Position **DeadLinkFinder** as the essential zero-dependency CLI & GitHub Action for offline Markdown (`.md`) and reStructuredText (`.rst`) link graph verification, GitHub Flavored Markdown (GFM) `#heading-anchor` integrity, and native SARIF v2.1.0 Code Scanning.
>
> Live Repository: [https://github.com/umutgungorr/deadlinkfinder](https://github.com/umutgungorr/deadlinkfinder)  
> PyPI Package: `pip install deadlinkfinder` / `uvx deadlinkfinder`  
> GitHub Marketplace Action: `uses: umutgungorr/deadlinkfinder@v1`

---

## 📅 High-Impact Launch Schedule (Timing Blueprint)

| Platform | Recommended Day & Time (EST) | Turkey Time (TRT / UTC+3) | Target Community & Tone |
|---|---|---|---|
| **Hacker News (Show HN)** | Tuesday or Wednesday, 08:30–09:00 AM EST | 15:30–16:00 | Open-source maintainers, docs engineers, zero-dependency fans |
| **Reddit (`r/Python`)** | Tuesday or Wednesday, 10:30 AM EST | 17:30 | Python developers, Sphinx/RST & Markdown authors, CLI builders |
| **Reddit (`r/devops`)** | Wednesday or Thursday, 09:30 AM EST | 16:30 | CI/CD architects, GitHub Actions & Code Scanning users |
| **X / Twitter (Global)** | Simultaneous with HN (Tue 09:00 AM EST) | 16:00 | Side-by-side terminal comparison & SARIF Code Scanning showcase |
| **LinkedIn (Global & TR)** | Wednesday, 11:00 AM EST | 18:00 | Staff engineers, DevRel leads, documentation platform owners |

---

## 1. 🟠 Hacker News (Show HN)

### Title Options
1. **Recommended**: `Show HN: DeadLinkFinder – Zero-dependency Markdown & RST link, image, and #anchor verifier with SARIF`
2. **Alternative A**: `Show HN: DeadLinkFinder – Offline documentation link graph & GFM heading anchor checker in pure Python`
3. **Alternative B**: `Show HN: DeadLinkFinder – Stop shipping broken #heading-anchors and missing docs assets in <15ms`

---

### First Comment (OP Introduction — Post Immediately After Submitting)

```markdown
Hey HN! I built DeadLinkFinder because documentation rot happens silently in almost every repository:

1. Someone renames a section heading from `## Setup & Installation` to `## Quick Start`, breaking 8 cross-file `[setup](docs/guide.md#setup--installation)` links across the repo.
2. Someone moves a diagram out of `assets/` or refactors a folder structure, leaving broken relative links and missing images (`![Arch](assets/arch.png)`).
3. Existing link checkers either hammer external servers on every PR (causing flaky CI failures from rate-limits), ignore GitHub Flavored Markdown `#heading-anchor` slug rules (emojis, duplicate `-1`/`-2` counters), or only support Markdown while ignoring Python's reStructuredText (`.rst`) and Sphinx roles (`:doc:`, `:ref:`).

DeadLinkFinder (`deadlinkfinder`) is a zero-dependency CLI written entirely in the Python standard library (`re`, `pathlib`, `difflib`, `hashlib`, `json`, `urllib`) that treats your docs as an offline link graph:

- 🔗 **Dual-Format Link Graph (`.md` & `.rst`)**: Validates standard Markdown links, HTML `<a href>`/`<img src>`, reStructuredText inline links (`` `Text <path.rst>`_ ``), directives (`.. image::`, `.. figure::`), and Sphinx roles (`:doc:`, `:ref:`, `:download:`).
- ⚓ **Exact GFM Heading Anchor Engine**: Reproduces GitHub's heading slug algorithm—handling emojis, punctuation stripping, inline formatting, and duplicate heading counters (`#features`, `#features-1`, `#features-2`) for both same-file and cross-file anchors.
- 💡 **Fuzzy "Did You Mean?" Suggestions**: Uses `difflib` against the repository file tree to suggest the exact moved or misspelled path when a relative link breaks (`DLF-001`).
- 🛡️ **Native OASIS SARIF v2.1.0 Output**: Emits deterministic `partialFingerprints` (`primaryLocationLineHash`) so broken links appear inline on GitHub Pull Requests via Code Scanning without duplicate alert spam.
- ⚡ **100% Offline by Default (<15ms startup)**: Zero network calls unless `--check-external` is explicitly passed. Runs anywhere on Python 3.9–3.14 via `uvx deadlinkfinder`.

Repo & GitHub Action: https://github.com/umutgungorr/deadlinkfinder

Would love your feedback and edge cases!
```

---

## 2. 🔴 Reddit Launch Posts

### A. Subreddit: `r/Python`
**Title**: `I built DeadLinkFinder: A zero-dependency Markdown (.md) & reStructuredText (.rst) link, image, and #heading-anchor verifier in pure Python`  
**Flair**: `Project` / `Showcase`

**Body**:
```markdown
Hi r/Python!

While maintaining several Python packages and documentation trees mixing `README.md`, `docs/*.md`, and Sphinx `.rst` files, I kept running into broken cross-file `#heading-anchor` links and moved image paths that slipped through CI.

I built **DeadLinkFinder** (https://github.com/umutgungorr/deadlinkfinder) — a fast, zero-dependency documentation integrity verifier built strictly with the Python standard library (Python 3.9–3.14).

### What makes it different:
- **Both Markdown & reStructuredText**: Checks `[text](path.md#slug)`, `![alt](img.png)`, RST hyperlinks, `.. image::`, `.. figure::`, and Sphinx `doc` / `ref` / `download` roles.
- **GFM Anchor Slug Verification**: Validates same-file and cross-file `#heading-anchors`, including emoji stripping and duplicate heading counters (`#section-1`, `#section-2`).
- **Code Block Isolation**: Automatically ignores sample links inside fenced code blocks (` ``` `), RST `.. code-block::` directives, and inline code spans.
- **Fuzzy Path Suggestions**: Suggests the closest file in your repo when a link target is renamed or typo'd.
- **SARIF v2.1.0 + JSON + Text**: Integrates directly with GitHub Code Scanning (`DLF-001` through `DLF-007`).

Try it instantly without installing:
```bash
uvx deadlinkfinder .
```

Or install via pip:
```bash
pip install deadlinkfinder
```

Feedback and PRs are very welcome!
```

### B. Subreddit: `r/devops`
**Title**: `DeadLinkFinder: Fast, offline-first documentation link & #anchor gate for GitHub Actions and Code Scanning (SARIF v2.1.0, 0 dependencies)`

**Body**:
```markdown
Most CI link checkers fail in production pipelines for one of two reasons:
1. They make live HTTP requests on every PR and fail randomly due to external rate limits (HTTP 429/403).
2. They pull in 300MB of Node/Ruby/Docker dependencies just to check local relative paths.

I built **DeadLinkFinder** (https://github.com/umutgungorr/deadlinkfinder) as a deterministic, offline-by-default CI quality gate (`<15ms` cold start, zero dependencies):

- **Offline Link Graph by Default**: Verifies local relative links, image assets (`DLF-004`), and cross-file `#heading-anchors` (`DLF-002`) across `.md` and `.rst` files in milliseconds with zero network flakiness.
- **Native SARIF v2.1.0**: Generates `partialFingerprints` (`primaryLocationLineHash`) for `github/codeql-action/upload-sarif@v3` so broken doc links annotate the exact PR line.
- **Drop-in GitHub Action**: `uses: umutgungorr/deadlinkfinder@v1` or `pre-commit` hook.
- **Optional External Mode**: Run `--check-external --timeout 5.0` on a scheduled nightly cron job instead of blocking PR merges on third-party downtime.

GitHub: https://github.com/umutgungorr/deadlinkfinder
```

---

## 3. 🌐 X / Twitter Launch Thread

```text
🔗 Tired of renaming a Markdown heading and silently breaking 10 cross-file #anchor links across your docs?

Meet DeadLinkFinder 🔍 — A zero-dependency CLI & GitHub Action that verifies your Markdown (.md) & reStructuredText (.rst) link graph, images, and GFM #anchors in <15ms.

Pure Python stdlib. Native SARIF v2.1.0.

🧵👇
```

```text
2/ What it catches offline in milliseconds:
• DLF-001: Broken relative links + fuzzy "Did you mean?" file suggestions
• DLF-002: Missing same-file or cross-file #heading-anchors (emojis & -1/-2 duplicates supported!)
• DLF-004: Missing local image/diagram assets
• DLF-005: Empty or malformed link targets

Run anywhere instantly:
$ uvx deadlinkfinder .

https://github.com/umutgungorr/deadlinkfinder
```

---

## 4. 💼 LinkedIn Post

```text
Documentation is part of your software's public API—yet broken relative links, missing architecture diagrams, and dead #heading-anchors slip through code review every day.

Today I'm open-sourcing DeadLinkFinder (v0.2.2): a zero-dependency documentation link graph and GFM anchor integrity verifier written in pure Python (3.9–3.14).

Key engineering highlights:
• Offline-First Speed (<15ms startup): Verifies local file links, images, and cross-file #heading-anchors across both Markdown (.md) and reStructuredText (.rst / Sphinx) without flaky external network calls.
• Fuzzy Remediation: Automatically suggests the closest matching repository path when files are moved or renamed.
• Native GitHub Code Scanning: Emits OASIS SARIF v2.1.0 with deterministic SHA-256 partial fingerprints for inline PR annotations.
• Zero External Dependencies: Built strictly on the Python standard library.

Try it in one command:
uvx deadlinkfinder .

Repository: https://github.com/umutgungorr/deadlinkfinder
Case Study: https://umutgungorr.com/projects/deadlinkfinder

#OpenSource #Python #DevOps #Documentation #DeveloperExperience #CICD #GitHubActions
```

# Contributing to DeadLinkFinder

Thank you for your interest in contributing to **DeadLinkFinder**! We welcome improvements, bug reports, feature suggestions, and pull requests.

---

## 🛠️ Development Setup

DeadLinkFinder is built with **zero external runtime dependencies** using the Python standard library. It supports Python 3.9 through 3.14.

```bash
# Clone the repository
git clone https://github.com/umutgungorr/deadlinkfinder.git
cd deadlinkfinder

# Install editable development build with uv
uv pip install -e .
```

---

## 🧪 Running Tests & Quality Checks

We maintain a strict 100% test pass rate across all operating systems:

```bash
# Run full pytest suite
uv run --with pytest pytest contract_tests tests -v

# Run Ruff linter
uv run --with ruff ruff check .

# Run Ruff format check
uv run --with ruff ruff format --check .
```

---

## 📝 Pull Request Guidelines

1. Ensure all 32+ tests pass locally before submitting.
2. Maintain zero external runtime dependencies (`dependencies = []` in `pyproject.toml`).
3. Add unit tests for any new edge case (e.g. GFM heading anchor slug rule, reStructuredText directive, or SARIF field).
4. Follow the existing clean Python code style and include type hints.

---

## 📜 Code of Conduct

Please review and respect our [Code of Conduct](CODE_OF_CONDUCT.md) in all community interactions.

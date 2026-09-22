# Contributing to DeadLinkFinder

Thank you for helping improve DeadLinkFinder! Contributions are warmly appreciated.

## Development Setup

DeadLinkFinder has **zero external dependencies** and uses Python 3.12+ stdlib exclusively.

```bash
# Clone the repository
git clone https://github.com/umutgungorr/deadlinkfinder.git
cd deadlinkfinder

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install editable package with dev dependencies
pip install -e .
pip install pytest ruff
```

## Running Tests & Linters

```bash
# Run test suite
pytest tests contract_tests -v

# Run linter
ruff check .
```

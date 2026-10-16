# Changelog

All notable changes to this project will be documented in this file.

## [v0.2.2] - 2026-10-16
### Added
- Full Python 3.9–3.14 compatibility via `slotted_dataclass` compatibility layer (`deadlinkfinder.compat`).
- Cross-platform GitHub Actions CI matrix (`ubuntu-latest`, `windows-latest`, `macos-latest` across Python 3.9–3.14) and composite Action verification workflow (`test-action.yml`).
- Full reStructuredText (`.rst`) and Sphinx role (`doc`, `ref`, `download`) link, image, and section anchor verification alongside GitHub Flavored Markdown (`.md`).
- Community health standards (`CODE_OF_CONDUCT.md`, updated `CONTRIBUTING.md`, and `LAUNCH_KIT.md`).

## [v0.2.1] - 2026-09-23
### Added
- Live terminal demonstration block in README.
- PyPI packaging configuration (`deadlinkfinder`) with zero runtime dependencies.
- Local Markdown link, heading anchor, image reference validator, and external URL checker.
- SARIF export format support for GitHub Code Scanning integration.

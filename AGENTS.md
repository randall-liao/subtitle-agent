# AI Agent Instructions (Table of Contents)

Welcome! This repository follows an **agent-native** development model. You must read and follow the documentation in `docs/`. This file is just a map. 

## System of Record (`docs/`)
- [Core Beliefs](docs/design-docs/core-beliefs.md) - Our "golden principles" and agent-first mindset.
- [Architecture & Boundaries](ARCHITECTURE.md) - Strict domain boundaries and package layering.
- [Quality Grades](docs/QUALITY_SCORE.md) - The current technical debt and quality report card.
- [Execution Plans](docs/exec-plans/) - Where we store our tactical roadmaps.

## ✅ Agent Rules & Conventions

1. **Use `uv` strictly**: Use `uv run <command>`, `uv add <package>`, or `uv add --dev <package>`.
2. **DO NOT MODIFY CLI TOOLS**: The files in `src/cli/` (`subdl_cli.py` and `tmdb_cli.py`) are external/upstream code. They **MUST NOT** be modified, and they are intentionally excluded from all testing.

## 🚀 Common Commands

- **Dependencies**: `uv sync`
- **Lint**: `uv run ruff check . --fix`, `uv run ruff format .`
- **Typecheck**: `uv run pyright`
- **Test**: `uv run pytest`

If you are modifying our documentation or architecture, ensure you run the custom linters:
- `uv run python scripts/lint_docs.py`
- `uv run python scripts/lint_architecture.py`

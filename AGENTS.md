# AI Agent Instructions (AGENTS.md)

Welcome! This repository follows an **agent-native** development model. Your primary goal is to help maintain and extend this repository efficiently while adhering to our strict conventions.

## 🛠 Core Tech Stack

- **Python**: `python >= 3.14`
- **Package Manager**: `uv` (Use `uv add`, `uv run`, `uv sync`)
- **Agent Framework**: `google-adk`
- **Typing & Validation**: `pydantic`
- **Linter & Formatter**: `ruff`
- **Type Checker**: `pyright` (Strict mode)
- **Testing**: `pytest`
- **Security Check**: `gitleaks`

## 📁 Repository Structure

- `src/subtitle_agent/` - Main application code.
- `tests/` - All unit and integration tests.
- `docs/` - Architectural documentation:
  - `docs/architecture.md` - High-level system design.
  - `docs/conventions.md` - Coding and style conventions.
  - `docs/debt.md` - Known technical debt.
  - `docs/runbook.md` - Operational guides.

## ✅ Agent Rules & Conventions

1. **Use `uv` strictly**: Never use `pip` natively. Use `uv run <command>`, `uv add <package>`, or `uv add --dev <package>`.
2. **Strict Typing**: All code must pass `pyright` in strict mode. Use comprehensive type hints. Never use `Any` if a more specific type can be applied.
3. **Format & Lint**: Ensure all code passes `uv run ruff check .` and `uv run ruff format .`.
4. **Test Everything**: All new logic must be accompanied by tests in the `tests/` directory. Run tests locally using `uv run pytest` before committing.
5. **No Direct Pushes to Main**: Branch protection is enabled. Push your work to a branch and submit a Pull Request. PRs do not require human approval to merge if checks pass, but you must open one.

## 🚀 Common Commands

*   **Install/Sync dependencies**: `uv sync --all-extras --dev`
*   **Run Linter**: `uv run ruff check . --fix`
*   **Run Formatter**: `uv run ruff format .`
*   **Run Typechecker**: `uv run pyright`
*   **Run Tests**: `uv run pytest`
*   **Security Scan**: `pre-commit run gitleaks --all-files`

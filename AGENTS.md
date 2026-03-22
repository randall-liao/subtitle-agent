# AI Agent Instructions (AGENTS.md)

Welcome! This repository follows an **agent-native** development model. Your primary goal is to help maintain and extend this repository efficiently while adhering to our strict conventions.

## 🛠 Core Tech Stack

- **Python**: `python >= 3.14`
- **Package Manager**: `uv` (Use `uv add`, `uv run`, `uv sync`)
- **CLI Tools**: Focus on `src/cli/subdl_cli.py` and `src/cli/tmdb_cli.py`.
- **Typing & Validation**: `pydantic`
- **Linter & Formatter**: `ruff`
- **Type Checker**: `pyright` (Strict mode)
- **Testing**: `pytest`

## 📁 Repository Structure

- `src/cli/` - CLI application code.
- `tests/` - Unit and integration tests.
- `docs/` - Project documentation.

## ✅ Agent Rules & Conventions

1. **Use `uv` strictly**: Never use `pip` natively. Use `uv run <command>`, `uv add <package>`, or `uv add --dev <package>`.
2. **Strict Typing**: All code must pass `pyright` in strict mode. Use comprehensive type hints.
3. **Format & Lint**: Ensure all code passes `uv run ruff check .` and `uv run ruff format .`.
4. **Test Everything**: All new logic must be accompanied by tests.
5. **DO NOT MODIFY CLI TOOLS**: The files in `src/cli/` (`subdl_cli.py` and `tmdb_cli.py`) are external/upstream code. They **MUST NOT** be modified, and they are intentionally excluded from all testing and coverage requirements.
6. **Pass All Checks**: If any code changes occur, the agent MUST run and pass all checks (`ruff`, `pyright`, `pytest`) before concluding the task.

## 🚀 Common Commands

*   **Install/Sync dependencies**: `uv sync`
*   **Run Linter**: `uv run ruff check . --fix`
*   **Run Formatter**: `uv run ruff format .`
*   **Run Typechecker**: `uv run pyright`
*   **Run Tests**: `uv run pytest`

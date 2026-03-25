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
3. **Reason, Don't Guess**: We no longer use rigid Python regex to match subtitles. Use the `download_and_extract` tool to inspect ZIP contents and use your internal reasoning to pick the best file.
4. **ADK-Powered Agent**: The agent is defined declaratively using the [Google Agent Development Kit (ADK)](https://github.com/google/adk-python). The `Agent` class in `src/agent/prompt_logic.py` defines the agent with its tools. ADK's native tool-calling loop handles orchestration — the LLM autonomously decides which tools to call and in what order.
5. **Feature Branch & PR Workflow**: You are strictly forbidden from pushing code directly to the `main` branch. You must always create a feature branch and a Pull Request for any changes.

## 🚀 Common Commands

- **Dependencies**: `uv sync`
- **Lint**: `uv run ruff check . --fix`, `uv run ruff format .`
- **Typecheck**: `uv run pyright`
- **Test**: `uv run pytest`

If you are modifying our documentation or architecture, ensure you run the custom linters:
- `uv run python scripts/lint_docs.py`
- `uv run python scripts/lint_architecture.py`

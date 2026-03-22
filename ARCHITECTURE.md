# Architecture

The Subtitle Agent codebase is heavily structured to allow deterministic agent navigation. 

## Strict Dependency Layering
We enforce forward-only dependencies mechanically. The layers are:
1. `src/cli/` (External/Upstream)
2. `src/core/` (Utility/Logic)
3. `src/agent/` (AI Prompting & Tools)
4. `src/main.py` (Entrypoint)

**Rules:**
- `src/cli/` has ZERO internal dependencies. It cannot import from `core`, `agent`, or `main`.
- `src/core/` can only depend on standard library or external packages. It cannot import from `cli` or `agent`.
- `src/agent/` can import from `core` and `cli`.
- `src/main.py` can import from anything.

These boundaries are mechanically enforced by `scripts/lint_architecture.py`.

## Domains
- **SubDL API**: `src/cli/subdl_cli.py`
- **TMDB API**: `src/cli/tmdb_cli.py`
- **File Discovery**: `src/core/discovery.py`
- **Security Check**: `src/core/security.py`

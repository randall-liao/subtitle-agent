# Architecture

The Subtitle Agent codebase is heavily structured to allow deterministic agent navigation. 

## Strict Dependency Layering
We enforce forward-only dependencies mechanically. The layers are:
1. `src/cli/` (External/Upstream)
2. `src/core/` (Utility/Logic)
3. `src/agent/` (ADK Agent Definition & Tools)
4. `src/main.py` (Entrypoint — ADK `InMemoryRunner`)

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
- **Agent Definition**: `src/agent/prompt_logic.py` (ADK `Agent` with instruction + tools)
- **Intelligent Retrieval**: `src/agent/tools.py` (Atomic: `search_tmdb`, `get_movie_details`, `search_subdl`, `download_and_extract`, `copy_to_media_library`)

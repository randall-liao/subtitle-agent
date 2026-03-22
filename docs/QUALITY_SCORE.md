# Quality Grades

We track the quality of our domains to know where our "AI slop" or technical debt is highest.

| Domain | Layer | Grade | Notes / Debt |
|---|---|---|---|
| `cli/subdl_cli.py` | CLI | A | Upstream code, excluded from coverage requirements. |
| `cli/tmdb_cli.py` | CLI | A | Upstream code, excluded from coverage requirements. |
| `core/discovery.py` | Core | B+ | Missing broader extension support beyond hardcoded lists. |
| `core/security.py` | Core | A | High confidence, but OS paths could be tricky on Windows. |
| `agent/prompt_logic.py` | Agent | B | Instructions are solid, but could use structured outputs instead of raw text checking. |

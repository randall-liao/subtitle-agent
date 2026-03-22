# System Design

## Core Philosophy
Subtitle Agent bridges robust procedural scripting with probabilistic LLM reasoning.

We use **Large Language Models (Google Gemini)** primarily for *heuristic routing and semantic parsing*, keeping heavy file I/O out of the model's direct responsibility. We construct deterministic Python boundaries that the LLM invokes via function calling. By doing this, we offload the "fuzzy" problem (parsing scene release names, matching season/episode pairs) to the LLM, but maintain strict control over actual network and disk operations.

---

## Detailed Feature Mechanics

The following sections document exactly how the current features in the codebase are implemented under this agent-first philosophy.

### 1. Automatic Discovery & Parsing (`core.discovery`)
When the user points the agent at a root media folder, we don't just process everything blindly:
- The `is_video_file()` function dynamically identifies targets using python's `mimetypes.guess_type()`. If a file lacks MIME metadata, it falls back to a hardcoded extension set (`.mp4`, `.mkv`, etc.).
- A recursive `find_videos_missing_subtitles()` generator streams through the target directory. It checks whether an adjacent subtitle file already exists, skipping files that are already satisfied.
- The state of discovery is strictly tied to the filesystem. There are no relational databases.

### 2. Prompt Logic & Agentic Search (`agent.prompt_logic`)
Instead of regex-based scrapers (which frequently fail on mislabeled scene releases), we pass the raw video filename to the Gemini model.
- The `SYSTEM_PROMPT` enforces a strict sequence: Parse the filename -> Search TMDB for the correct IMDB ID -> Search SubDL using that IMDB ID -> Download the Zip archive -> Extract the final subtitle.
- This creates semantic flexibility. A file named `s_show.1x03.720p.mkv` will correctly be interpreted as Season 1, Episode 3 by the model.

### 3. Deep Metadata Integration (TMDB + SubDL)
Rather than writing our own scrapers, we leverage tested upstream CLI libraries under `src/cli/`.
- **TMDB Tool (`search_tmdb`, `get_movie_details`)**: We provide the LLM a tool to query the TMDB API. If the model is uncertain about a TV show's exact ID, it searches TMDB first to lock in the official IMDB ID.
- **SubDL Tool (`download_subtitle_with_subdl`)**: With the confirmed IMDB ID and the user's requested language, the model calls the SubDL API to download the `.zip` archive holding the raw subtitles.

### 4. Workspace Isolation & Safe Extraction
Downloading unknown `.zip` archives from the internet introduces severe security risks.
- **Ephemeral Workspaces**: We download all files to an isolated `/tmp/subtitle_agent_workspace/` directory to prevent zip-bomb / directory-traversal pollution in the user's primary media folder.
- **Deterministic Validation**: The LLM calls `extract_and_copy_subtitle()`. This function parses the `.zip` using Python's standard library. It then extracts only files matching `.srt` or `.ass`.
- **Safe Payload Delivery (`core.security`)**: The `safe_copy` module enforces `pathlib.resolve(strict=True)` boundaries. It guarantees that the final moving of the `.srt` file into the user's media library is mathematically confined to the intended target directory, shutting down any `../../` traversal attempts.

### 5. Configurable Execution (CLI)
The `src/main.py` entrypoint is an `argparse` wrapper that sets the initial configuration:
- `--language` is a required string. It is dynamically interpolated into the LLM's system prompt so the agent strictly searches for that linguistic flag in SubDL.
- `--model` allows the user to hot-swap Gemini versions (defaulting to the fast `gemini-3.1-flash-lite-preview`).
- Standard, colorful, actionable outputs are generated for the end-user via the `loguru` library to convey progress without exposing python tracebacks or complex json tool calls.

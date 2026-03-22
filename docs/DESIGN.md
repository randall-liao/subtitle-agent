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

### 2. Prompt Logic & Autonomous Orchestration (`agent.prompt_logic`)
Instead of regex-based scrapers (which frequently fail on mislabeled scene releases) and rigid Python `for` loops, we pass the **entire list** of missing video filenames to the Gemini model in a single prompt.
- **Autonomous Looping**: The model orchestrates its own execution loop. It is instructed to process every video in the queue, handling api tool calls and iterative searches entirely on its own.
- **Strategic Planning**: The `SYSTEM_PROMPT` enforces an `<orchestration_model>`. Before making an API call, the agent must output a `<plan>` block detailing context, required metadata, and its API strategy, providing human-like semantic reasoning for its actions.
- This creates semantic flexibility. A file named `s_show.1x03.720p.mkv` will correctly be interpreted as Season 1, Episode 3 by the model.

### 3. Deep Metadata Integration (TMDB + SubDL)
Rather than writing our own scrapers, we leverage tested upstream CLI libraries under `src/cli/`.
- **TMDB Tool (`search_tmdb`, `get_movie_details`)**: We provide the LLM a tool to query the TMDB API. **Strict TMDB-First Requirement**: The LLM is heavily instructed to *always* query TMDB first to lock in an official IMDB/TMDB ID because SubDL's fuzzy text search is notoriously unreliable.
- **Atomic SubDL Tool (`search_subdl`)**: The LLM calls the SubDL API with its confirmed metadata (`tmdb_id` or `imdb_id`, Season, Episode, Year). This returns a JSON array of potential subtitle matches. The LLM uses its reasoning to pick the best match (e.g., matching release groups or special editions).

### 4. Workspace Isolation & Intelligent Extraction
Downloading unknown archives from the internet introduces security risks.
- **Ephemeral Workspaces**: We download all files to an isolated `/tmp/subtitle_agent_workspace/` directory to prevent zip-bomb / directory-traversal pollution in the user's primary media folder.
- **Intelligent Filename Matching (`download_and_extract`)**: This tool downloads and unpacks the chosen URL. Crucially, it returns a list of *all* extracted filenames to the LLM. The LLM then uses its full contextual intelligence to select the specific `.srt` that matches the current video (essential for season packs).
- **Safe Payload Delivery (`copy_to_media_library`)**: The LLM provides the specific extracted path. The system then renames and moves it safely. This module enforces `pathlib.resolve(strict=True)` boundaries to guarantee moves are mathematically confined to the intended target directory.

### 5. Configurable Execution (CLI)
The `src/main.py` entrypoint is an `argparse` wrapper that sets the initial configuration:
- `--language` is a required string. It is dynamically interpolated into the LLM's system prompt so the agent strictly searches for that linguistic flag in SubDL.
- `--model` allows the user to hot-swap Gemini versions (defaulting to the fast `gemini-3.1-flash-lite-preview`).
- **Session reporting**: At the end of the autonomous execution session, `main.py` generates colorful, actionable reports via `loguru` to convey progress.

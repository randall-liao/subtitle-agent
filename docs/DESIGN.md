# System Design

## Philosophy
Subtitle Agent bridges robust procedural scripting with probabilistic LLM reasoning.

We use **Large Language Models (Google Gemini)** primarily for *heuristic routing and semantic parsing*, keeping heavy file I/O out of the model's direct responsibility. We construct deterministic Python boundaries that the LLM invokes via function calling.

## Key Design Decisions
1. **Tool Independence:** The upstream API integrations (TMDB, SubDL) are fully isolated in `src/cli/`. This allows us to transparently swap them out or upgrade them without modifying the agent's core prompt logic.
2. **Workspace Isolation:** Subtitles are typically packaged in `.zip` archives. The agent downloads files to an ephemeral `/tmp/subtitle_agent_workspace/`, keeping extraction pollution away from the user's permanent media directory until a valid `.srt/.ass/.vtt` is confirmed.
3. **Stateless Runs:** Each run dynamically crawls the directory searching for video signatures (MIME guessing + extension fallback). There is no heavy SQLite metadata database to maintain, meaning the application is radically portable.

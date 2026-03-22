# Spec: Autonomous Subtitle Agent

## The Problem
Previous iterations of the Subtitle Agent forced the LLM into rigid Python `for` loops (processing videos 1-by-1 or in arbitrary batches of 5). This caused two major issues:
1. **Quota Exhaustion**: Initializing a new Gemini context for every video rapidly hit `429 RESOURCE_EXHAUSTED` limits.
2. **Context Loss**: The agent could not look at the entire directory of missing subtitles to make heuristic deductions (e.g. noticing that 10 videos all belong to the same Season Pack).

## The Spec
The Subtitle Agent MUST operate under a **fully autonomous orchestration model**. Python loops are strictly forbidden for agentic tasks. 

**Behavioral Requirements:**
1. **Total Queue Ingestion**: `src/main.py` must gather ALL missing subtitles and supply the entire string array to the LLM in a single initialization prompt.
2. **Agent Self-Looping**: The LLM is responsible for iteratively calling tools on every file in its queue before concluding the turn.
3. **Strategic Planning (`<plan>`)**: Before the agent is allowed to invoke `search_subdl` or `search_tmdb`, it must output a semantic `<plan>` block detailing its exact strategy for that specific video (e.g. diagnosing a failed IMDB lookup and falling back to a raw film-name search).
4. **Intelligent File Extraction**: The agent must never use regex or index-guessing to pick a subtitle from a `.zip` file. It must use the atomic `download_and_extract` tool to inspect the raw file array, and then use strict string matching via `copy_to_media_library` to place the final `.srt`.

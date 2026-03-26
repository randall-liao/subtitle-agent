# ADK Integration Deep Dive

This document explains how the **Google Agent Development Kit (ADK)** is integrated into the Subtitle Agent project to handle autonomous tool orchestration.

## 🏗️ Structural Overview

The migration to ADK replaced a manual `while` loop that managed chat turns with a declarative `Agent` and a managed `Runner`.

```mermaid
graph TD
    subgraph "CLI Layer (src/main.py)"
        M[Entrypoint] -->|1. Discovery| D[Discovery Engine]
        M -->|2. Initialize| A[ADK Agent]
        M -->|3. Start| R[InMemoryRunner]
    end
    
    subgraph "ADK Layer (src/agent/)"
        A -->|Defines| I[Agent Instruction]
        A -->|Registers| T[Tools]
        R -.-|Manages Loop| A
    end
    
    subgraph "Runtime (Google ADK Engine)"
        R <-->|API Calls| L[Gemini LLM]
        R -->|Execute| T
        T -->|Search/Metadata/Files| EXT[External APIs / Disk]
    end

    style A fill:#e1bee7,stroke:#8e24aa,stroke-width:2px
    style R fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    style L fill:#bbdefb,stroke:#1976d2,stroke-width:2px
```

## 🔄 Agentic Execution Flow

When you run `uv run src/main.py`, the following sequence occurs inside the ADK runtime. ADK abstracts the "thinking" and "doing" turns, allowing the LLM to decide the best path to find subtitles.

```mermaid
sequenceDiagram
    autonumber
    participant M as main.py (Entrypoint)
    participant R as InMemoryRunner (ADK)
    participant L as Gemini LLM
    participant T as Tools (src/agent/tools.py)

    M->>R: runner.run(user_prompt)
    
    rect rgb(240, 240, 240)
        Note over R,L: ADK Tool-Calling Loop
        R->>L: Current state + Prompt
        L-->>R: call: search_tmdb(title="...")
        R->>T: execute search_tmdb
        T-->>R: returns movie_metadata
        R->>L: Observation: movie_metadata
        
        L-->>R: call: search_subdl(tmdb_id="...")
        R->>T: execute search_subdl
        T-->>R: returns list_of_subtitles
        R->>L: Observation: list_of_subtitles
        
        L-->>R: call: download_and_extract(url="...")
        R->>T: execute download_and_extract
        T-->>R: returns extracted_files
        R->>L: Observation: extracted_files
    end

    L-->>R: Final Answer: "Processed file.srt"
    R-->>M: yield Event(FinalResponse)
    M->>M: Final Verification on Disk (Core Security)
```

## 💎 Key Benefits of ADK

1.  **Deterministic Looping**: We no longer write `while True: chat.send_message()`. ADK handles retries, tool call resolution, and event streaming.
2.  **Native Function Calling**: ADK automatically converts Python type hints (e.g., `tmdb_id: str`) and docstrings into Gemini tool schemas.
3.  **Simplified Instruction**: The system instruction (in `prompt_logic.py`) no longer needs to explain *how* to call tools or provide XML planning tags. It just defines the *what* and the *rules*.
4.  **In-Memory State**: `InMemoryRunner` maintains a lightweight session history, allowing the agent to "remember" previous tool failures (e.g., if search by TMDB ID fails, it can try searching by title in the next turn).

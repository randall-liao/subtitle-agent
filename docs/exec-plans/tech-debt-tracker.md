# Technical Debt Tracker

This document tracks identified areas in the codebase that require refactoring or improvement.

| Issue | Severity | Component | Description |
|---|---|---|---|
| Rigid Subtitle Extensions | Low | `core.discovery` | Expanding MIME type guessing beyond `.srt` and `.ass` rather than maintaining hardcoded arrays. |
| Structured Prompt Logic | Medium | `agent.prompt_logic` | Converting loosely coupled `System Instruction` strings into fully typed Pydantic structures for Gemini tool calling. |
| CLI Tool Abstractions | Low | `cli/` | Abstracting SubDL/TMDB REST calls into a unified interface so upstream API changes don't fracture our agent tools. |

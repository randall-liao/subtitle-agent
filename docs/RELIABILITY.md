# Reliability & Telemetry

Subtitle Agent focuses on maintaining consistency even when external APIs or zip extraction fail.

## LLM Verification
We use explicit retry routines when parsing unstructured filenames to handle model hallucinations. Tool prompts strictly enforce `required` parameters (like language and TMDB ID) to increase structured adherence.

## Observability
All CLI interactions are logged via `loguru`. During runs, success/failure ratios are aggregated at the end of each **batch** (5 videos) and presented as a final summary report:
- `SuccessCount`: Number of successfully extracted and safely moved subtitle tracks in the session.
- `FailureCount`: Number of videos still missing subtitles after the agent session completes.

These logs can be hooked strictly into `stdout` for background automated processing (cron jobs, systemd services) without requiring interactive terminal prompts.

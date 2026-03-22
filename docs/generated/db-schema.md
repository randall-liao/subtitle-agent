# Database Schema

As per our architecture (`ARCHITECTURE.md`), Subtitle Agent is completely **stateless**.

There are NO relational, document, or graph databases maintained by this tool. The sole state resides within the host's filesystem (specifically, via the `.subtitle_agent_files` manifest created in the target media root for security tracking).

No `.sql`, SQLite, or schema migrations exist in this repository.

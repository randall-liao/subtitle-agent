# Product Sense

**The Problem:**
Home Theater PC (HTPC) users, Plex administrators, and media hoarders frequently download videos that do not include embedded subtitle tracks. Manually navigating to ad-ridden subtitle websites, searching for the correct movie release, guessing the sync, and downloading/extracting `.srt` files is an incredibly massive friction point.

**The Solution:**
Subtitle Agent entirely removes the human from the loop. By pointing an AI tool at a local directory, the agent autonomously discovers missing subtitles, searches SubDL using proper linguistic API flags, and downloads the best match. 

**Target Audience:**
- Non-technical end-users who just want to watch their localized TV shows.
- Power-users running media servers (Jellyfin/Plex) who want 100% automated subtitle coverage via CLI tools.

**Core Value Proposition:**
- Fast execution.
- LLM heuristics for messy filenames instead of brittle regex scrapers.
- Local execution with strong sandbox guarantees.

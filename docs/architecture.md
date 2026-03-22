# Architecture

The Subtitle Agent CLI is a set of independent Python scripts designed for media management.

## Components

### 1. `subdl_cli.py`
Connects to SubDL via REST API to:
- Search for subtitles.
- Download and filter subtitle content.

### 2. `tmdb_cli.py`
Connects to TMDB to search for media metadata, facilitating easier search by IMDB ID.

# Subtitle Agent CLI 🎬

A collection of CLI tools to find, download, and organize subtitles for your media collection using OpenSubtitles and TMDB.

## 🚀 Overview

Subtitle Agent CLI provides direct tools for subtitle management:
- **`subdl_cli.py`**: A powerful tool to search and download subtitles from OpenSubtitles.org.
- **`tmdb_cli.py`**: A tool to search for movie and TV show information on TMDB.

## ✨ Features

- **OpenSubtitles Integration**: Search subtitles by file hash, IMDB ID, or search string.
- **TMDB Search**: Quickly find movie metadata and IMDB IDs.
- **Support for Many Languages**: Search in multiple languages simultaneously.
- **Customizable Output**: Format downloaded subtitle filenames to match your preferences.

## 📋 Prerequisites

- **Python**: `>= 3.14`
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **API Access**: An OpenSubtitles account (for `subdl_cli.py`) and a TMDB API key (if applicable for `tmdb_cli.py`).

## 🛠 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/randall-liao/subtitle-agent.git
   cd subtitle-agent
   ```

2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```

## 🚀 Usage

### Subtitle Search and Download

Run the subtitle CLI:
```bash
uv run src/cli/subdl_cli.py --lang eng /path/to/your/video.mp4
```

### TMDB Search

Run the TMDB CLI:
```bash
uv run src/cli/tmdb_cli.py --query "The Matrix"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](file:///home/devuser/projects/subtitle-agent/LICENSE) file for details.

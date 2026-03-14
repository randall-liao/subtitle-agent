# Subtitle Agent 🎬

An automated agent powered by Gemini and OpenSubtitles to find and organize subtitles for your media collection.

## 🚀 Overview

Subtitle Agent simplifies the process of finding subtitles for your videos. It recursively scans a directory for media files, uses Gemini's intelligence to determine search queries, searches OpenSubtitles via its REST API, and automatically downloads and renames the best matches to match your video filenames.

## ✨ Features

- **Gemini Powered**: Uses LLM heuristics to identify video files and formulate accurate search queries.
- **OpenSubtitles REST API**: Direct integration with OpenSubtitles API for subtitle search and download.
- **Recursive Scanning**: Finds media files across nested directories.
- **Model Selection**: Choose from available Gemini models for the task.
- **Safe Operations**: Copies and renames subtitles without modifying your original video files.
- **Hash-Based Search**: Supports file hash calculation for accurate subtitle matching.

## 📋 Prerequisites

- **Python**: `>= 3.14`
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **API Key**: A valid [Gemini API Key](https://aistudio.google.com/).

## 🛠 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/randall-liao/subtitle-agent.git
   cd subtitle-agent
   ```

2. Install dependencies using `uv`:
   ```bash
   uv sync --all-extras --dev
   ```

## ⚙️ Configuration

Set your Gemini API key as an environment variable:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

## 🚀 Usage

Run the agent by specifying the target directory:

```bash
uv run src/subtitle_agent/main.py --dir /path/to/your/videos
```

### Arguments:
- `--dir`: (Required) Starting directory for subtitle search.
- `--language`: (Optional) Desired subtitle language (e.g., `en`, `zh`). Default is `en`.
- `--instructions`: (Optional) Custom instructions for subtitle selection.

Example with custom language and instructions:
```bash
uv run src/subtitle_agent/main.py --dir ./movies --language zh --instructions "prefer traditional Chinese"
```

## 🤖 Development

This project follows an **agent-native** development model. For contribution guidelines, repository structure, and development commands, please refer to [AGENTS.md](file:///home/devuser/projects/subtitle-agent/AGENTS.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](file:///home/devuser/projects/subtitle-agent/LICENSE) file for details.

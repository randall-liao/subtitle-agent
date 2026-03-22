# Subtitle Agent 🎬

An AI agent that automatically finds, downloads, and organizes subtitles for your media collection using SubDL and TMDB.

## 🚀 Usage

Run the Subtitle Agent by pointing it to a directory containing your video files. The agent will automatically scan for videos missing subtitles and download the best matches.

```bash
uv run src/main.py --language "English" /path/to/your/media/folder
```

### Options

- `folder`: Directory to scan for missing subtitles.
- `--language`: (Required) Natural language for the subtitles (e.g., English, French, Spanish). The agent automatically converts this to the appropriate API flag.
- `--model`: Optionally specify the Gemini model to use (defaults to `gemini-3.1-flash-lite-preview`).

## 🔑 API Keys Setup

To use the Subtitle Agent, you need to set up the following API keys in your environment (e.g., in a `.env` file):

1. **Gemini API Key (`GEMINI_API_KEY`)**
   - Go to Google AI Studio ([aistudio.google.com](https://aistudio.google.com/)).
   - Sign in and click "Get API key" on the left navigation to generate a new key.

2. **SubDL API Key (`SUBDL_API_KEY`)**
   - Go to [subdl.com](https://subdl.com/) and create an account.
   - After signing in, navigate to your account settings or profile page to generate and copy your API Key.

3. **TMDB API Key (`TMDB_API_KEY`)**
   - Go to [themoviedb.org](https://www.themoviedb.org/) and create an account.
   - Go to your Account Settings > API.
   - Request a "Developer" API key and fill in the required details. Once approved, copy the API Key (v3 auth).

## 🚀 Overview

Subtitle Agent uses Google's Gemini models to intelligently analyze your media library and find the best matching subtitles:
- **Automatic Discovery**: Scans directories for video files missing subtitles.
- **Agentic Search**: Uses LLM capabilities to search and select the best subtitles.

> **Note**: The CLI files in `src/cli/` are considered external/upstream code. They are not to be modified and are excluded from testing and coverage calculations.

## ✨ Features

- **SubDL Integration**: Search subtitles by IMDB ID, or search string.
- **TMDB Search**: Quickly find movie metadata and IMDB IDs.
- **Support for Many Languages**: Search in multiple languages simultaneously.
- **Customizable Output**: Format downloaded subtitle filenames to match your preferences.

## 📋 Prerequisites

- **Python**: `>= 3.14`
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](file:///home/devuser/projects/subtitle-agent/LICENSE) file for details.

## Credits

Special thanks to the authors of the CLI tools used in this project:
- **SubDL CLI**: [@kalmnoise](https://github.com/kalmnoise/subdl_api_cli)
- **TMDB CLI**: [@illegalbyte](https://github.com/illegalbyte/TMDB_CLI)

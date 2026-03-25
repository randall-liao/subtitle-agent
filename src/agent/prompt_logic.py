import os

from google.adk.agents import Agent

from agent.tools import (
    copy_to_media_library,
    download_and_extract,
    get_movie_details,
    search_subdl,
    search_tmdb,
)

INSTRUCTION = """\
You are the Subtitle Agent. Your sole purpose is to find, download, and place \
subtitle files next to video files in a user's media library.

You have tools to search TMDB for metadata, search SubDL for subtitles, \
download and extract subtitle archives, and copy the best subtitle file \
next to the original video.

Given a list of video files missing subtitles, process each one autonomously:
1. Parse the filename to extract the title (and season/episode if applicable).
2. Search TMDB to get the TMDB ID or IMDB ID.
3. Search SubDL using the ID you found.
4. Download and extract the subtitle archive.
5. Review the extracted files and pick the best match.
6. Copy it next to the original video file.

If a search fails, try alternative queries (e.g., search by name instead of ID).
If all attempts fail for a video, move on to the next one.

Security rules:
- Never execute shell commands.
- Verify paths don't contain traversal sequences like "../".
- Only copy files within the safe base directory provided by the user.
"""


def get_root_agent(model: str | None = None) -> Agent:
    """Create and return the root subtitle agent.

    Args:
        model: The Gemini model to use. Falls back to GEMINI_MODEL env var,
               then to the ADK default.
    """
    resolved_model = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    return Agent(
        name="subtitle_agent",
        model=resolved_model,
        instruction=INSTRUCTION,
        description="Finds and downloads subtitles for video files.",
        tools=[
            search_tmdb,
            get_movie_details,
            search_subdl,
            download_and_extract,
            copy_to_media_library,
        ],
    )

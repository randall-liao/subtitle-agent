import logging
import os
import zipfile
from pathlib import Path

import requests

from core.security import safe_copy

WORKSPACE_DIR = Path("/tmp/subtitle_agent_workspace")


def search_tmdb(query: str, search_type: str = "multi") -> list[dict[str, str]]:
    """Search TMDB for a movie or TV show by name.

    Args:
        query: The name of the movie or TV show.
        search_type: The type of search (e.g., 'movie', 'tv', 'multi').
    """

    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        raise RuntimeError("TMDB_API_KEY not found in environment.")

    url = f"https://api.themoviedb.org/3/search/{search_type}?api_key={api_key}&query={query}"
    response = requests.get(url)
    response.raise_for_status()
    results = response.json().get("results", [])

    return [
        {
            "id": str(r.get("id")),
            "title": str(r.get("title") or r.get("name") or ""),
            "media_type": str(r.get("media_type") or search_type),
            "release_date": str(r.get("release_date") or r.get("first_air_date") or ""),
        }
        for r in results
    ][:5]


def get_movie_details(tmdb_id: str) -> dict[str, str | int | float | list[str]]:
    """Get full details of a movie, including its IMDB ID."""

    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        raise RuntimeError("TMDB_API_KEY not found in environment.")

    url = (
        f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}&language=en-US"
    )
    response = requests.get(url)
    response.raise_for_status()
    movie_dict = response.json()

    return {
        "title": movie_dict.get("title", ""),
        "imdb_id": movie_dict.get("imdb_id", ""),
        "release_date": movie_dict.get("release_date", ""),
    }


def search_subdl(
    language: str,
    imdb_id: str | None = None,
    film_name: str | None = None,
    season_number: int | None = None,
    episode_number: int | None = None,
    type: str | None = None,
    year: int | None = None,
) -> list[dict]:
    """Search for subtitles on SubDL using explicit metadata.

    Args:
        language: The 2-letter language code (e.g., 'EN') or comma-separated list like 'EN,FA'.
        imdb_id: The IMDB ID string (e.g., 'tt1234567'), optional.
        film_name: Name of the film/show to search for.
        season_number: Season number for TV shows.
        episode_number: Episode number for TV shows.
        type: 'movie' or 'tv'.
        year: Release year.

    Returns:
        List of subtitles objects (top 5 max). Each object contains 'release_name', 'url', 'season', 'episode'.
    """
    from cli.subdl_cli import search_subtitles

    api_key = os.environ.get("SUBDL_API_KEY")
    if not api_key:
        raise RuntimeError("SUBDL_API_KEY environment variable is required.")

    kwargs = {
        "api_key": api_key,
        "languages": language,
        "subs_per_page": 5,
        "imdb_id": imdb_id,
        "film_name": film_name,
        "season_number": season_number,
        "episode_number": episode_number,
        "type": type,
        "year": year,
    }
    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    logging.info(f"Searching subdl with kwargs: {kwargs}")
    result = search_subtitles(**kwargs)

    if not result.get("status") or not result.get("subtitles"):
        return []

    subtitle_list = result.get("subtitles")
    if not isinstance(subtitle_list, list):
        return []

    return [
        {
            "release_name": sub.get("release_name", ""),
            "url": sub.get("url", ""),
            "season": sub.get("season"),
            "episode": sub.get("episode"),
            "author": sub.get("author", ""),
        }
        for sub in subtitle_list[:5]
    ]


def download_and_extract(url: str) -> list[str]:
    """Download a subtitle zip or file from a SubDL URL and extract it to a temporary workspace.

    Args:
        url: The exact SubDL URL string returned from `search_subdl` (e.g., '/subtitle/1234-5678.zip').

    Returns:
        A list of absolute paths to all extracted subtitle files (.srt, .ass, etc.) inside the workspace.
        You MUST review this list to find the best matching file.
    """
    import time

    from cli.subdl_cli import LINK_PREFIX

    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

    full_url = LINK_PREFIX + url if url.startswith("/") else url
    logging.info(f"Downloading subtitle from {full_url}")

    prefix = str(int(time.time() * 1000))
    zip_path = WORKSPACE_DIR / f"{prefix}_download.zip"

    response = requests.get(full_url)
    response.raise_for_status()
    with open(zip_path, "wb") as f:
        f.write(response.content)

    extracted_files = []

    if zip_path.suffix.lower() == ".zip" or zip_path.suffix.lower() == ".rar":
        # Note: simplistic extraction assuming zip-like signature for this agent demo
        # SubDL largely returns Zips.
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                extract_dir = WORKSPACE_DIR / f"{prefix}_extracted"
                extract_dir.mkdir(exist_ok=True)
                zip_ref.extractall(extract_dir)
                for file in extract_dir.rglob("*"):
                    if file.is_file() and file.suffix.lower() in {
                        ".srt",
                        ".ass",
                        ".ssa",
                        ".vtt",
                    }:
                        extracted_files.append(str(file.absolute()))
        except zipfile.BadZipFile:
            # Maybe it wasn't a zip after all
            extracted_files.append(str(zip_path.absolute()))
    else:
        extracted_files.append(str(zip_path.absolute()))

    return extracted_files


def copy_to_media_library(
    extracted_subtitle_path: str, original_video_path: str, safe_base_dir: str
) -> str:
    """Safely copy the EXACT chosen extracted subtitle file to the user's media library.
    It will be automatically renamed to match the original video.

    Args:
        extracted_subtitle_path: The exact path you selected from the `download_and_extract` tool's output.
        original_video_path: The absolute path of the original video file.
        safe_base_dir: The allowed root directory for the media library.

    Returns:
        The path to the newly copied subtitle file.
    """
    import shutil

    downloaded = Path(extracted_subtitle_path)
    video = Path(original_video_path)

    if not downloaded.exists():
        raise FileNotFoundError(f"Selected file {downloaded} does not exist.")

    final_subtitle_name = f"{video.stem}{downloaded.suffix}"
    final_temp_path = WORKSPACE_DIR / final_subtitle_name

    shutil.copy2(downloaded, final_temp_path)

    target_path = video.parent / final_subtitle_name
    safe_copy(final_temp_path, target_path, safe_base_dir)

    return str(target_path)

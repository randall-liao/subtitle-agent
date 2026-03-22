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


def download_subtitle_with_subdl(
    video_file_name: str, language: str, imdb_id: str | None = None
) -> str:
    """Download a subtitle for a given video using SubDL into the workspace.

    Args:
        video_file_name: The name of the original video file (e.g., 'Movie.2023.mkv').
        imdb_id: The IMDB ID string (e.g., 'tt1234567'), optional.
        language: The 2-letter language code (e.g., 'EN') or comma-separated list like 'EN,FA'.

    Returns:
        The path to the downloaded file (.srt, .ass, or .zip) in the workspace.
    """
    from cli.subdl_cli import LINK_PREFIX, search_subtitles

    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    api_key = os.environ.get("SUBDL_API_KEY")
    if not api_key:
        raise RuntimeError("SUBDL_API_KEY environment variable is required.")

    # Call the new search_subtitles method
    kwargs = {
        "api_key": api_key,
        "languages": language,
        "subs_per_page": 5,
    }
    if imdb_id:
        kwargs["imdb_id"] = imdb_id
    else:
        # If no imdb_id, let's just supply the file_name
        kwargs["file_name"] = video_file_name

    logging.info(f"Searching subdl with kwargs: {kwargs}")
    result = search_subtitles(**kwargs)

    if not result.get("status") or not result.get("subtitles"):
        raise FileNotFoundError("Subtitle was not found by subdl_cli.")

    # Get the top subtitle result
    subtitle_list = result.get("subtitles")
    if not isinstance(subtitle_list, list) or not subtitle_list:
        raise FileNotFoundError("No subtitles found in result.")

    subtitle = subtitle_list[0]
    download_url = subtitle.get("url")
    if not download_url:
        raise FileNotFoundError("Subtitle result missing download URL.")

    full_url = LINK_PREFIX + download_url
    logging.info(f"Downloading subtitle from {full_url}")

    # Download it into WORKSPACE_DIR
    # Wait, sometimes it might be .srt or .rar. Subdl usually serves ZIP.
    # We will just write it to a zip file in the workspace
    dummy_video_path = WORKSPACE_DIR / video_file_name
    dummy_video_path.touch(exist_ok=True)

    stem = dummy_video_path.stem
    zip_path = WORKSPACE_DIR / f"{stem}.zip"

    response = requests.get(full_url)
    response.raise_for_status()
    with open(zip_path, "wb") as f:
        f.write(response.content)

    return str(zip_path)


def extract_and_copy_subtitle(
    downloaded_path: str, original_video_path: str, safe_base_dir: str
) -> str:
    """Extract (if zipped) a subtitle, rename to match the video, and safely copy it.

    Args:
        downloaded_path: The path to the downloaded subtitle.
        original_video_path: The absolute path of the original video file.
        safe_base_dir: The allowed root directory for the media library.

    Returns:
        The path to the newly copied subtitle file.
    """
    downloaded = Path(downloaded_path)
    video = Path(original_video_path)

    if not downloaded.exists():
        raise FileNotFoundError(f"Downloaded file {downloaded} does not exist.")

    extracted_file_path = downloaded
    if downloaded.suffix.lower() == ".zip":
        with zipfile.ZipFile(downloaded, "r") as zip_ref:
            extract_dir = WORKSPACE_DIR / f"{video.stem}_extracted"
            extract_dir.mkdir(exist_ok=True)
            zip_ref.extractall(extract_dir)
            for file in extract_dir.rglob("*"):
                if file.is_file() and file.suffix.lower() in {
                    ".srt",
                    ".ass",
                    ".ssa",
                    ".vtt",
                }:
                    extracted_file_path = file
                    break
            else:
                raise FileNotFoundError(
                    "Could not find a subtitle file in ZIP archive."
                )

    final_subtitle_name = f"{video.stem}{extracted_file_path.suffix}"
    final_temp_path = WORKSPACE_DIR / final_subtitle_name

    # Using safe_copy explicitly from temp to target
    import shutil

    shutil.copy2(extracted_file_path, final_temp_path)

    target_path = video.parent / final_subtitle_name
    safe_copy(final_temp_path, target_path, safe_base_dir)

    return str(target_path)

# pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType, reportUnknownParameterType, reportAny]
import hashlib
import shutil
import tempfile
from pathlib import Path

import httpx


def find_video_files(directory: str, extensions: list[str] | None = None) -> list[str]:
    """Recursively search for video files in the given directory matching given extensions."""
    if extensions is None or not extensions:
        raise ValueError(
            "Please provide a list of video extensions to search for (e.g. ['.mkv', '.mp4'])"
        )

    video_extensions = {ext if ext.startswith(".") else f".{ext}" for ext in extensions}
    videos = []
    base_path = Path(directory)
    if not base_path.exists():
        return videos

    for path in base_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in video_extensions:
            videos.append(str(path))

    return videos


def safe_copy_and_rename_subtitle(
    src_path: str, dest_dir: str, new_name: str, allowed_base_dir: str
) -> bool:
    """Safely copies a subtitle file from src_path to dest_dir with new_name, ensuring it stays within allowed_base_dir."""
    src = Path(src_path)
    if not src.exists() or not src.is_file():
        raise FileNotFoundError(f"Source subtitle file {src_path} does not exist.")

    dest_d = Path(dest_dir).resolve()
    base_d = Path(allowed_base_dir).resolve()

    # Check boundary escape
    if not dest_d.is_relative_to(base_d):
        raise PermissionError(
            f"Destination {dest_d} is outside the allowed directory {base_d}"
        )

    dest_path = dest_d / new_name

    # Do not overwrite video files, only copy
    if dest_path.suffix.lower() in {".mkv", ".mp4", ".avi"}:
        raise ValueError("Cannot overwrite video files.")

    shutil.copy2(src, dest_path)
    return True


def calculate_file_hash(file_path: str) -> str:
    """Calculate the hash of a file for OpenSubtitles API."""
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File {file_path} does not exist.")

    # OpenSubtitles uses a specific hash algorithm (first and last 64KB)
    file_size = path.stat().st_size
    if file_size < 128 * 1024:
        # File too small, just hash entire file
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    chunk_size = 64 * 1024
    with open(path, "rb") as f:
        head = f.read(chunk_size)
        f.seek(-chunk_size, 2)
        tail = f.read(chunk_size)

    combined = head + tail
    return hashlib.md5(combined).hexdigest()


def search_subtitles(
    query: str | None = None,
    imdb_id: str | None = None,
    file_hash: str | None = None,
    languages: str = "en",
) -> list[dict]:
    """Search for subtitles on OpenSubtitles REST API.

    Args:
        query: Search query (movie/show name)
        imdb_id: IMDB ID (e.g., 'tt1234567')
        file_hash: File hash for hash-based search
        languages: Language code (e.g., 'en', 'zh')

    Returns:
        List of subtitle results with file_id, name, language, etc.
    """
    api_url = "https://api.opensubtitles.com/api/v1/subtitles"
    headers = {
        "Accept": "application/json",
        "Api-Key": "",  # Optional for basic search
    }

    params: dict[str, str] = {"languages": languages}

    if query:
        params["query"] = query
    if imdb_id:
        params["moviehash"] = imdb_id
    if file_hash:
        params["moviehash"] = file_hash

    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(api_url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("data", []):
                attributes = item.get("attributes", {})
                files = attributes.get("files", [])
                if files:
                    results.append(
                        {
                            "file_id": files[0].get("file_id"),
                            "file_name": files[0].get("file_name", "unknown"),
                            "name": attributes.get("release", "Unknown"),
                            "language": attributes.get("language", "unknown"),
                            "score": attributes.get("score", 0),
                        }
                    )
            return results
    except httpx.HTTPError as e:
        return [{"error": f"Search failed: {e}"}]


def download_subtitle(file_id: str, dest_dir: str | None = None) -> str:
    """Download a subtitle from OpenSubtitles by file_id.

    Args:
        file_id: The file ID from search_subtitles results
        dest_dir: Optional destination directory (defaults to temp dir)

    Returns:
        Path to the downloaded subtitle file
    """
    api_url = "https://api.opensubtitles.com/api/v1/download"
    headers = {
        "Accept": "application/json",
        "Api-Key": "",  # Optional for basic download
    }

    try:
        with httpx.Client(follow_redirects=True) as client:
            # First get the download link
            response = client.post(
                api_url,
                headers=headers,
                json={"file_id": file_id},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            download_link = data.get("link")

            if not download_link:
                return "Error: No download link received"

            # Download the actual subtitle file
            sub_response = client.get(download_link, headers=headers, timeout=30.0)
            sub_response.raise_for_status()

            # Determine destination
            if dest_dir:
                dest_path = Path(dest_dir) / f"subtitle_{file_id}.srt"
            else:
                temp_dir = Path(tempfile.mkdtemp(prefix="subtitle_dl_"))
                dest_path = temp_dir / f"subtitle_{file_id}.srt"

            # Write subtitle content
            content = sub_response.text
            dest_path.write_text(content, encoding="utf-8")

            return str(dest_path)
    except httpx.HTTPError as e:
        return f"Error: Download failed: {e}"

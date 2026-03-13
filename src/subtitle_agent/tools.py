# pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType, reportUnknownParameterType, reportAny]
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


def download_and_extract_subtitle(url: str) -> list[str]:
    """Downloads a subtitle archive from the given URL and extracts it, returning valid subtitle paths."""
    # assrt requires User-Agent if they restrict, but let's try basic httpx
    # Need to handle rar or zip
    temp_dir = Path(tempfile.mkdtemp(prefix="subtitle_dl_"))

    headers = {"User-Agent": "Mozilla/5.0"}
    with httpx.Client(follow_redirects=True, headers=headers) as client:
        resp = client.get(url)
        resp.raise_for_status()

        # Determine extension from Content-Disposition or url
        cd = resp.headers.get("Content-Disposition", "")
        suffix = ".rar" if "rar" in cd.lower() or ".rar" in url.lower() else ".zip"

        archive_path = temp_dir / f"downloaded_archive{suffix}"
        with open(archive_path, "wb") as f:
            f.write(resp.content)

    # Use patool or shutil to extract
    extract_dir = temp_dir / "extracted"
    extract_dir.mkdir()

    # Find extracted subtitles
    sub_exts = {".srt", ".ass", ".ssa", ".vtt"}
    subs = []

    try:
        import patoolib  # type: ignore

        patoolib.extract_archive(str(archive_path), outdir=str(extract_dir))
    except Exception as e:
        # Fallback to shutil
        try:
            shutil.unpack_archive(str(archive_path), extract_dir)
        except shutil.ReadError:
            # Maybe it is a subtitle already natively downloaded as text
            if "srt" in cd.lower() or "ass" in cd.lower():
                return [str(archive_path)]
            print(f"Extraction failed: {e}")
            return []

    for path in extract_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in sub_exts:
            subs.append(str(path))

    return subs

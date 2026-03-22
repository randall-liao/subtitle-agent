import mimetypes
import os
from pathlib import Path

VIDEO_EXTENSIONS = {".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"}
SUBTITLE_EXTENSIONS = {".srt", ".ass", ".ssa", ".vtt"}


def is_video_file(path: Path) -> bool:
    """Determine if a file is a video using MIME types, then falling back to common extensions."""
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type and mime_type.startswith("video/"):
        return True

    # Fallback to extension check
    return path.suffix.lower() in VIDEO_EXTENSIONS


def is_subtitle_file(path: Path) -> bool:
    """Determine if a file is a subtitle using MIME types and extensions."""
    mime_type, _ = mimetypes.guess_type(path)
    # text/plain is sometimes guessed for srt
    if (
        mime_type in ("application/x-subrip", "text/vtt", "text/plain")
        and path.suffix.lower() in SUBTITLE_EXTENSIONS
    ):
        return True

    return path.suffix.lower() in SUBTITLE_EXTENSIONS


def find_videos_missing_subtitles(
    root_dir: str | os.PathLike[str],
) -> tuple[int, list[Path]]:
    """Recursively find video files that do not have an acompanying subtitle."""
    root = Path(root_dir)
    videos: list[Path] = []
    subtitles_by_dir_and_stem: set[tuple[Path, str]] = set()

    # Pre-scan for all subtitles
    for root_path, _, files in os.walk(root):
        rpath = Path(root_path)
        for f in files:
            fpath = rpath / f
            if is_subtitle_file(fpath):
                subtitles_by_dir_and_stem.add((rpath, fpath.stem))

    total_videos = 0
    # Scan for videos
    for root_path, _, files in os.walk(root):
        rpath = Path(root_path)
        for f in files:
            fpath = rpath / f
            if is_video_file(fpath):
                total_videos += 1
                if (rpath, fpath.stem) not in subtitles_by_dir_and_stem:
                    videos.append(fpath)

    return total_videos, videos

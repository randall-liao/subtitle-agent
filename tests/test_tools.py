from pathlib import Path

import pytest

from subtitle_agent.tools import (
    find_video_files,
    safe_copy_and_rename_subtitle,
)


def test_find_video_files(tmp_path: Path):
    # Create dummy files
    (tmp_path / "movie1.mkv").touch()
    (tmp_path / "movie2.mp4").touch()
    (tmp_path / "document.txt").touch()

    # Create nested dummy files
    sub_dir = tmp_path / "season1"
    sub_dir.mkdir()
    (sub_dir / "episode1.avi").touch()

    # Pass explicit extensions
    videos = find_video_files(str(tmp_path), [".mkv", ".mp4", ".avi"])
    assert len(videos) == 3
    assert any("movie1.mkv" in v for v in videos)
    assert any("movie2.mp4" in v for v in videos)
    assert any("episode1.avi" in v for v in videos)
    assert not any("document.txt" in v for v in videos)


def test_safe_copy_and_rename_subtitle(tmp_path: Path):
    src_dir = tmp_path / "downloads"
    src_dir.mkdir()
    src_file = src_dir / "downloaded.srt"
    src_file.write_text("subtitle content")

    dest_dir = tmp_path / "movies"
    dest_dir.mkdir()

    # Valid copy
    success = safe_copy_and_rename_subtitle(
        src_path=str(src_file),
        dest_dir=str(dest_dir),
        new_name="movie.srt",
        allowed_base_dir=str(tmp_path),
    )
    assert success is True
    assert (dest_dir / "movie.srt").exists()

    # Boundary violation
    outside_dir = tmp_path.parent
    with pytest.raises(PermissionError):
        safe_copy_and_rename_subtitle(
            src_path=str(src_file),
            dest_dir=str(outside_dir),
            new_name="movie.srt",
            allowed_base_dir=str(tmp_path),
        )

    # Overwrite video protection
    (dest_dir / "movie.mkv").touch()
    with pytest.raises(ValueError):
        safe_copy_and_rename_subtitle(
            src_path=str(src_file),
            dest_dir=str(dest_dir),
            new_name="movie.mkv",
            allowed_base_dir=str(tmp_path),
        )

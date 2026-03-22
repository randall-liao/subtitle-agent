from pathlib import Path

from core.discovery import (
    find_videos_missing_subtitles,
    is_subtitle_file,
    is_video_file,
)


def test_is_video_file(tmp_path: Path):
    video = tmp_path / "test.mkv"
    assert is_video_file(video) is True

    txt = tmp_path / "test.txt"
    assert is_video_file(txt) is False


def test_is_subtitle_file(tmp_path: Path):
    sub = tmp_path / "test.srt"
    assert is_subtitle_file(sub) is True

    video = tmp_path / "test.mkv"
    assert is_subtitle_file(video) is False


def test_find_videos_missing_subtitles(tmp_path: Path):
    # Dummy video missing subtitle
    (tmp_path / "video1.mkv").touch()

    # Dummy video with subtitle
    (tmp_path / "video2.mp4").touch()
    (tmp_path / "video2.srt").touch()

    # Dummy other file
    (tmp_path / "info.txt").touch()

    total, missing = find_videos_missing_subtitles(tmp_path)
    assert total == 2
    assert len(missing) == 1
    assert missing[0].name == "video1.mkv"

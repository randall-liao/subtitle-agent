from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent.tools import (
    WORKSPACE_DIR,
    download_subtitle_with_subdl,
    extract_and_copy_subtitle,
    get_movie_details,
    search_tmdb,
)


@patch("agent.tools.requests.get")
@patch.dict("os.environ", {"TMDB_API_KEY": "fake_key"})
def test_search_tmdb(mock_get: MagicMock):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [{"id": 123, "title": "Test", "media_type": "movie"}]
    }
    mock_get.return_value = mock_response

    res = search_tmdb("Test")
    assert res[0]["id"] == "123"


@patch("agent.tools.requests.get")
@patch.dict("os.environ", {"TMDB_API_KEY": "fake_key"})
def test_get_movie_details(mock_get: MagicMock):
    mock_response = MagicMock()
    mock_response.json.return_value = {"title": "Test", "imdb_id": "tt123"}
    mock_get.return_value = mock_response

    res = get_movie_details("123")
    assert res["title"] == "Test"


@patch("agent.tools.requests.get")
@patch("cli.subdl_cli.search_subtitles")
@patch.dict("os.environ", {"SUBDL_API_KEY": "fake_key"})
def test_download_subtitle_with_subdl(
    mock_search: MagicMock, mock_get: MagicMock, tmp_path: Path
):
    import shutil

    if WORKSPACE_DIR.exists():
        shutil.rmtree(WORKSPACE_DIR)

    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

    mock_search.return_value = {
        "status": True,
        "subtitles": [{"url": "/dummy_sub.zip"}],
    }

    mock_response = MagicMock()
    mock_response.content = b"fakezipdata"
    mock_get.return_value = mock_response

    res = download_subtitle_with_subdl("test.mkv", "tt123", "eng")
    assert res.endswith("test.zip")
    assert Path(res).exists()

    # Test failure mode
    mock_search.return_value = {"status": False}
    with pytest.raises(FileNotFoundError):
        download_subtitle_with_subdl("fail.mkv", "tt123", "eng")


@patch("cli.subdl_cli.search_subtitles")
@patch.dict("os.environ", {"SUBDL_API_KEY": "fake_key"})
def test_download_subtitle_with_subdl_missing_file(
    mock_search: MagicMock, tmp_path: Path
):
    import shutil

    if WORKSPACE_DIR.exists():
        shutil.rmtree(WORKSPACE_DIR)

    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    mock_search.return_value = {"status": False}
    with pytest.raises(FileNotFoundError):
        download_subtitle_with_subdl("missing.mkv", "tt123", "eng")


@patch("agent.tools.safe_copy")
@patch("agent.tools.zipfile.ZipFile")
def test_extract_and_copy_subtitle_flat(
    mock_zip: MagicMock, mock_copy: MagicMock, tmp_path: Path
):
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

    # Test flat srt
    srt_path = WORKSPACE_DIR / "test_copy.srt"
    srt_path.touch()

    video_path = tmp_path / "video.mkv"
    video_path.touch()

    res = extract_and_copy_subtitle(str(srt_path), str(video_path), str(tmp_path))
    assert res == str(tmp_path / "video.srt")


@patch("agent.tools.safe_copy")
@patch("agent.tools.zipfile.ZipFile")
def test_extract_and_copy_subtitle_zip(
    mock_zip: MagicMock, mock_copy: MagicMock, tmp_path: Path
):
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

    # Test zip
    zip_path = WORKSPACE_DIR / "test_copy.zip"
    zip_path.touch()

    # we need to simulate extraction since it uses extractall and checks filesystem
    def side_effect(extract_dir: Path):
        (Path(extract_dir) / "sub.srt").touch()

    mock_instance = MagicMock()
    mock_instance.extractall.side_effect = side_effect
    mock_zip.return_value.__enter__.return_value = mock_instance

    video_path = tmp_path / "video_zip.mkv"
    video_path.touch()

    res = extract_and_copy_subtitle(str(zip_path), str(video_path), str(tmp_path))
    assert res == str(tmp_path / "video_zip.srt")

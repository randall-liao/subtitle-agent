from pathlib import Path
from unittest.mock import MagicMock, patch

from agent.tools import (
    WORKSPACE_DIR,
    copy_to_media_library,
    download_and_extract,
    get_movie_details,
    search_subdl,
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


@patch("cli.subdl_cli.search_subtitles")
@patch.dict("os.environ", {"SUBDL_API_KEY": "fake_key"})
def test_search_subdl(mock_search: MagicMock):
    mock_search.return_value = {
        "status": True,
        "subtitles": [
            {
                "release_name": "Test Sub",
                "url": "/dummy.zip",
                "season": 1,
                "episode": 1,
            }
        ],
    }

    res = search_subdl("EN", imdb_id="tt123")
    assert len(res) == 1
    assert res[0]["url"] == "/dummy.zip"


@patch("agent.tools.requests.get")
def test_download_and_extract(mock_get: MagicMock, tmp_path: Path):
    import shutil

    if WORKSPACE_DIR.exists():
        shutil.rmtree(WORKSPACE_DIR)

    mock_response = MagicMock()
    mock_response.content = b"fakezipdata"
    mock_get.return_value = mock_response

    res = download_and_extract("/dummy.zip")
    assert len(res) == 1
    assert "download.zip" in res[0]


@patch("agent.tools.safe_copy")
def test_copy_to_media_library(mock_copy: MagicMock, tmp_path: Path):
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    srt_path = WORKSPACE_DIR / "test_copy.srt"
    srt_path.touch()

    video_path = tmp_path / "video.mkv"
    video_path.touch()

    res = copy_to_media_library(str(srt_path), str(video_path), str(tmp_path))
    assert res == str(tmp_path / "video.srt")

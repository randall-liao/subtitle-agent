from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from main import main


@patch(
    "main.sys.argv",
    ["main.py", "dummy_dir", "--model", "test-model", "--language", "English"],
)
@patch("main.sys.exit")
@patch("main.Path.is_dir")
@patch("main.find_videos_missing_subtitles")
@patch("main.InMemoryRunner")
@patch("main.get_root_agent")
def test_main_success(
    mock_get_agent: MagicMock,
    mock_runner_cls: MagicMock,
    mock_find: MagicMock,
    mock_check_dir: MagicMock,
    mock_exit: MagicMock,
    tmp_path: Path,
):
    mock_check_dir.return_value = True

    dummy_dir = tmp_path / "dummy_dir"
    dummy_dir.mkdir()

    video = dummy_dir / "test.mkv"
    video.touch()

    mock_find.return_value = (1, [video])

    mock_agent = MagicMock()
    mock_get_agent.return_value = mock_agent

    mock_runner = MagicMock()
    mock_runner_cls.return_value = mock_runner

    # simulate that the subtitle was created during the agent execution
    def run_side_effect(**kwargs: Any):
        (dummy_dir / "test.srt").touch()
        return iter([])

    mock_runner.run.side_effect = run_side_effect

    with patch("main.Path.resolve", return_value=dummy_dir):
        main()

    mock_exit.assert_not_called()


@patch(
    "main.sys.argv",
    ["main.py", "dummy_dir", "--model", "test-model", "--language", "English"],
)
@patch("main.sys.exit")
@patch("main.Path.is_dir")
@patch("main.find_videos_missing_subtitles")
@patch("main.InMemoryRunner")
@patch("main.get_root_agent")
def test_main_subtitle_not_found(
    mock_get_agent: MagicMock,
    mock_runner_cls: MagicMock,
    mock_find: MagicMock,
    mock_check_dir: MagicMock,
    mock_exit: MagicMock,
    tmp_path: Path,
):
    mock_check_dir.return_value = True

    dummy_dir = tmp_path / "dummy_dir"
    dummy_dir.mkdir()

    video = dummy_dir / "test.mkv"
    video.touch()

    mock_find.return_value = (1, [video])

    mock_agent = MagicMock()
    mock_get_agent.return_value = mock_agent

    mock_runner = MagicMock()
    mock_runner_cls.return_value = mock_runner
    mock_runner.run.return_value = iter([])

    with patch("main.Path.resolve", return_value=dummy_dir):
        main()

    mock_exit.assert_not_called()


@patch("main.sys.argv", ["main.py", "dummy_dir", "--language", "English"])
@patch("main.Path.is_dir")
@patch("main.find_videos_missing_subtitles")
@patch("main.InMemoryRunner")
@patch("main.get_root_agent")
def test_main_agent_processing_fail(
    mock_get_agent: MagicMock,
    mock_runner_cls: MagicMock,
    mock_find: MagicMock,
    mock_check_dir: MagicMock,
    tmp_path: Path,
):
    mock_check_dir.return_value = True
    dummy_dir = tmp_path / "dummy_dir"
    dummy_dir.mkdir()

    video = dummy_dir / "test.mkv"
    video.touch()

    mock_find.return_value = (1, [video])

    mock_agent = MagicMock()
    mock_get_agent.return_value = mock_agent

    mock_runner = MagicMock()
    mock_runner_cls.return_value = mock_runner
    mock_runner.run.side_effect = Exception("Agent generation failed")

    with patch("main.Path.resolve", return_value=dummy_dir):
        main()


@patch("main.sys.argv", ["main.py", "dummy_dir", "--language", "English"])
@patch("main.sys.exit", side_effect=SystemExit(1))
@patch("main.Path.is_dir")
def test_main_invalid_dir(mock_check_dir: MagicMock, mock_exit: MagicMock):
    mock_check_dir.return_value = False
    with pytest.raises(SystemExit):
        main()
    mock_exit.assert_called_with(1)


@patch("main.sys.argv", ["main.py", "dummy_dir", "--language", "English"])
@patch("main.sys.exit", side_effect=SystemExit(1))
@patch("main.Path.is_dir")
@patch("main.find_videos_missing_subtitles")
@patch("main.get_root_agent")
def test_main_agent_init_fail(
    mock_get_agent: MagicMock,
    mock_find: MagicMock,
    mock_check_dir: MagicMock,
    mock_exit: MagicMock,
    tmp_path: Path,
):
    mock_check_dir.return_value = True
    dummy_dir = tmp_path / "dummy_dir"
    dummy_dir.mkdir()

    mock_find.return_value = (1, [dummy_dir / "test.mkv"])
    mock_get_agent.side_effect = Exception("API Key missing")

    with patch("main.Path.resolve", return_value=dummy_dir), pytest.raises(SystemExit):
        main()

    mock_exit.assert_called_with(1)

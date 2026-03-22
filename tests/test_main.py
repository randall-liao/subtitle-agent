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
@patch("main.initialize_agent")
@patch("main.get_agent_tools")
@patch("main.GenerateContentConfig")
def test_main_success(
    mock_config: MagicMock,
    mock_tools: MagicMock,
    mock_init: MagicMock,
    mock_find: MagicMock,
    mock_check_dir: MagicMock,
    mock_exit: MagicMock,
    tmp_path: Path,
):
    mock_check_dir.return_value = True

    # We use a real dummy directory so Path operations don't fail
    dummy_dir = tmp_path / "dummy_dir"
    dummy_dir.mkdir()

    video = dummy_dir / "test.mkv"
    video.touch()

    mock_find.return_value = (1, [video])

    mock_client = MagicMock()
    mock_chat = MagicMock()
    mock_client.chats.create.return_value = mock_chat
    mock_init.return_value = mock_client

    # simulate that the subtitle was created during the agent execution
    def side_effect(*args: Any, **kwargs: Any):
        (dummy_dir / "test.srt").touch()

    mock_chat.send_message.side_effect = side_effect

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
@patch("main.initialize_agent")
@patch("main.get_agent_tools")
@patch("main.GenerateContentConfig")
def test_main_subtitle_not_found(
    mock_config: MagicMock,
    mock_tools: MagicMock,
    mock_init: MagicMock,
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

    mock_client = MagicMock()
    mock_chat = MagicMock()
    mock_client.chats.create.return_value = mock_chat
    mock_init.return_value = mock_client

    # simulate agent finishing without creating the srt file
    def side_effect(*args: Any, **kwargs: Any):
        pass

    mock_chat.send_message.side_effect = side_effect

    with patch("main.Path.resolve", return_value=dummy_dir):
        main()

    mock_exit.assert_not_called()


@patch("main.sys.argv", ["main.py", "dummy_dir", "--language", "English"])
@patch("main.Path.is_dir")
@patch("main.find_videos_missing_subtitles")
@patch("main.initialize_agent")
@patch("main.get_agent_tools")
@patch("main.GenerateContentConfig")
def test_main_agent_processing_fail(
    mock_config: MagicMock,
    mock_tools: MagicMock,
    mock_init: MagicMock,
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

    mock_client = MagicMock()
    mock_chat = MagicMock()
    mock_client.chats.create.return_value = mock_chat
    mock_init.return_value = mock_client

    # simulate an exception during the agent generation call
    mock_chat.send_message.side_effect = Exception("Agent generation failed")

    with patch("main.Path.resolve", return_value=dummy_dir):
        # We also need to capture stdout to verify the error was printed
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
@patch("main.initialize_agent")
def test_main_agent_init_fail(
    mock_init: MagicMock,
    mock_find: MagicMock,
    mock_check_dir: MagicMock,
    mock_exit: MagicMock,
    tmp_path: Path,
):
    mock_check_dir.return_value = True
    dummy_dir = tmp_path / "dummy_dir"
    dummy_dir.mkdir()

    mock_find.return_value = (1, [dummy_dir / "test.mkv"])
    mock_init.side_effect = Exception("API Key missing")

    with patch("main.Path.resolve", return_value=dummy_dir), pytest.raises(SystemExit):
        main()

    mock_exit.assert_called_with(1)

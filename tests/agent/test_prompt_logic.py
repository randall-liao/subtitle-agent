import os
from unittest.mock import MagicMock, patch

import pytest

from agent.prompt_logic import SYSTEM_PROMPT, get_agent_tools, initialize_agent


@patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
@patch("agent.prompt_logic.genai.Client")
def test_initialize_agent(mock_client: MagicMock):
    initialize_agent()
    mock_client.assert_called_with(api_key="test_key")


@patch.dict(os.environ, clear=True)
def test_initialize_agent_missing_key():
    with pytest.raises(ValueError):
        initialize_agent()


def test_get_agent_tools():
    tools = get_agent_tools()
    assert len(tools) == 5


def test_system_prompt():
    assert "Subtitle Agent" in SYSTEM_PROMPT
    assert "<system_role>" in SYSTEM_PROMPT
    assert "<security_protocols>" in SYSTEM_PROMPT
    assert "<orchestration_model>" in SYSTEM_PROMPT
    assert "<plan>" in SYSTEM_PROMPT

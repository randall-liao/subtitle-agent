import os
from unittest.mock import patch

from agent.prompt_logic import INSTRUCTION, get_root_agent


def test_get_root_agent_default_model():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
        agent = get_root_agent()
        assert agent.name == "subtitle_agent"
        assert len(agent.tools) == 5


def test_get_root_agent_custom_model():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
        agent = get_root_agent(model="gemini-2.0-flash")
        assert agent.name == "subtitle_agent"


def test_instruction_content():
    assert "Subtitle Agent" in INSTRUCTION
    assert "TMDB" in INSTRUCTION
    assert "SubDL" in INSTRUCTION
    assert "Security rules" in INSTRUCTION

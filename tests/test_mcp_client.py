# pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType, reportUnknownParameterType, reportMissingTypeArgument, reportAttributeAccessIssue]
import pytest

from subtitle_agent.mcp_client import MCPToolsWrapper


@pytest.mark.asyncio
async def test_mcp_client_mock():
    # If the local node/python script isn't running, this might fail, so we skip or test a dummy command
    wrapper = MCPToolsWrapper("python", ["-c", "print('dummy')"])
    # Not testing the actual connection in CI without an MCP server, but ensuring the object creation logic holds
    assert wrapper.server_params.command == "python"

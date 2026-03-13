# pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType, reportUnknownParameterType, reportMissingTypeArgument, reportAny]
from collections.abc import Callable
from typing import Any

from google.genai.types import FunctionDeclaration, Schema, Tool, Type
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPToolsWrapper:
    """Wraps an MCP StdioClient session and provides callable tools for the GenAI Agent."""

    def __init__(self, command: str, args: list[str]):
        self.server_params = StdioServerParameters(command=command, args=args)
        self.session: ClientSession | None = None
        self._exit_stack = None
        self._stdio = None

    async def __aenter__(self):
        from contextlib import AsyncExitStack

        self._exit_stack = AsyncExitStack()

        # Start stdio client
        read, write = await self._exit_stack.enter_async_context(
            stdio_client(self.server_params)
        )

        self.session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self.session.initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        if self._exit_stack:
            await self._exit_stack.aclose()

    async def get_tools(self) -> tuple[list[Tool], dict[str, Callable[..., Any]]]:
        """Fetch MCP tools and map them into Google GenAI format (Tool) and executable Callables."""
        if not self.session:
            raise RuntimeError(
                "MCP Session not initialized. Use within async context manager."
            )

        mcp_tools = await self.session.list_tools()
        genai_tools: list[Tool] = []
        callables: dict[str, Callable[..., Any]] = {}

        for tool in mcp_tools.tools:
            # Map JSON Schema to GenAI Schema correctly
            properties = {}
            required: list[str] = tool.inputSchema.get("required", [])
            for key, val in tool.inputSchema.get("properties", {}).items():
                if not isinstance(val, dict):
                    continue
                # simplified conversion, genai Schema wants Type enum
                type_val = Type.STRING
                if val.get("type") == "integer" or val.get("type") == "number":
                    type_val = Type.INTEGER
                elif val.get("type") == "boolean":
                    type_val = Type.BOOLEAN

                properties[key] = Schema(
                    type=type_val, description=val.get("description", "")
                )

            decl = FunctionDeclaration(
                name=tool.name,
                description=tool.description or "",
                parameters=Schema(
                    type=Type.OBJECT, properties=properties, required=required
                )
                if properties
                else None,
            )
            genai_tools.append(Tool(function_declarations=[decl]))

            # Create a bound async callable that invokes the tool on the MCP session
            def make_callable(tool_name: str) -> Callable[..., Any]:
                async def invoke(**kwargs: Any) -> str:
                    if not self.session:
                        return "Error: Session closed"
                    result = await self.session.call_tool(tool_name, arguments=kwargs)

                    if result.isError:
                        return f"Error: {result.content}"
                    return "\n".join(
                        str(getattr(c, "text", ""))
                        for c in result.content
                        if hasattr(c, "text")
                    )

                return invoke

            callables[tool.name] = make_callable(tool.name)

        return genai_tools, callables

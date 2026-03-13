# pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType, reportUnknownParameterType, reportDeprecated, reportArgumentType, reportAny]
import argparse
import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

import subtitle_agent.tools as safe_tools
from subtitle_agent.mcp_client import MCPToolsWrapper


async def main():
    parser = argparse.ArgumentParser(description="Subtitle Agent")
    parser.add_argument(
        "--dir", required=True, help="Starting directory for subtitle search"
    )
    parser.add_argument(
        "--language", default="en", help="Desired subtitle language (e.g. en, zh)"
    )
    parser.add_argument(
        "--instructions", default="", help="Custom instructions for subtitle selection"
    )

    args = parser.parse_args()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Please set GEMINI_API_KEY environment variable.")
        return

    start_dir = Path(args.dir).resolve()
    if not start_dir.exists():
        print(f"Directory {start_dir} does not exist.")
        return

    # Helper tools
    def list_media_files_tool(extensions: list[str]):
        """Recursively search for video files in the target directory matching the given extensions (e.g. ['mkv', 'mp4'])."""
        return safe_tools.find_video_files(str(start_dir), extensions)

    def safe_copy_and_rename_subtitle(src_path: str, new_name: str):
        """Safely copies a downloaded subtitle to the target directory with its new video-matching name."""
        return safe_tools.safe_copy_and_rename_subtitle(
            src_path, str(start_dir), new_name, str(start_dir)
        )

    # GenAI SDK Client
    client = genai.Client(api_key=api_key)

    try:
        available_models: list[str] = [
            str(m.name)
            for m in client.models.list()
            if m.name and "gemini" in str(m.name).lower()
        ]
        available_models = [m.replace("models/", "") for m in available_models if m]
    except Exception as e:
        print(f"Failed to fetch models: {e}")
        available_models = ["gemini-2.5-pro", "gemini-2.5-flash"]

    default_model = "gemini-3.1-flash-lite-preview"
    if default_model in available_models:
        available_models.remove(default_model)
    available_models.insert(0, default_model)

    print("\nAvailable Models:")
    for i, m_name in enumerate(available_models):
        print(f"{i + 1}. {m_name}")

    try:
        user_input = input(
            f"Select model [1-{len(available_models)}] (default=1): "
        ).strip()
        choice_idx = int(user_input) - 1 if user_input else 0
        if choice_idx < 0 or choice_idx >= len(available_models):
            choice_idx = 0
    except EOFError:
        choice_idx = 0
    except ValueError:
        choice_idx = 0

    selected_model = available_models[choice_idx]
    print(f"Selected: {selected_model}\n")

    print("Connecting to OpenSubtitles MCP proxy via npx stdio...")
    mcp_wrapper = MCPToolsWrapper(
        "npx",
        ["-y", "@opensubtitles/mcp-server@latest"],
    )
    mcp_wrapper.server_params.env = {**(os.environ), "MCP_MODE": "stdio"}

    async with mcp_wrapper as mcp:
        print("MCP Server connected.")
        genai_tools, mcp_callables = await mcp.get_tools()

        # Intercept the download_subtitle tool to prevent context bloat
        original_download = mcp_callables.get("download_subtitle")

        async def intercept_download_subtitle(**kwargs: Any):
            if not original_download:
                return "Error: download_subtitle not found in MCP tools"

            raw_result = await original_download(**kwargs)
            try:
                # the raw_result should be JSON str with { "content": subtitleContent, ... }
                data = json.loads(raw_result)
                if "content" in data and isinstance(data["content"], str):
                    # Save it temporarily
                    temp_dir = Path(tempfile.mkdtemp(prefix="subtitle_dl_"))
                    file_name = kwargs.get("file_name", "downloaded.srt")
                    temp_path = temp_dir / file_name
                    temp_path.write_text(data["content"], encoding="utf-8")

                    return f"Successfully downloaded and saved to temporary path: {temp_path}. You can now use safe_copy_and_rename_subtitle to move it."
            except Exception:
                pass

            return "Subtitle download processed. If it was raw content, it could not be saved correctly."

        mcp_callables["download_subtitle"] = intercept_download_subtitle

        # Build local tool declarations
        local_tools = [
            types.FunctionDeclaration(
                name="list_media_files_tool",
                description="Recursively search for video files in the target directory by providing a list of extensions (e.g. ['mkv', 'mp4']).",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "extensions": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.STRING),
                            description="List of file extensions to look for.",
                        )
                    },
                    required=["extensions"],
                ),
            ),
            types.FunctionDeclaration(
                name="safe_copy_and_rename_subtitle",
                description="Safely copies a downloaded subtitle to the target directory with its new video-matching name.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "src_path": types.Schema(
                            type=types.Type.STRING,
                            description="Absolute path to the downloaded subtitle file you want to keep.",
                        ),
                        "new_name": types.Schema(
                            type=types.Type.STRING,
                            description="The new filename for it (must match the video file exactly, except for the extension).",
                        ),
                    },
                    required=["src_path", "new_name"],
                ),
            ),
        ]

        all_callables = {
            "list_media_files_tool": list_media_files_tool,
            "safe_copy_and_rename_subtitle": safe_copy_and_rename_subtitle,
            **mcp_callables,
        }

        system_instruction = f"""You are a Subtitle Agent using OpenSubtitles.
Your tasks are:
1. Formulate a list of common video file extensions and pass them to list_media_files_tool to find missing subtitles.
2. For each media file, determine the best movie/TV show search query.
3. Use the OpenSubtitles 'search_subtitles' tool to find the subtitle. Pass 'languages': '{args.language}'.
   Remember you can search by 'query', 'imdb_id', or calculate file hash using 'calculate_file_hash'.
4. Download the best match using the 'download_subtitle' tool with the 'file_id' from the results.
5. The download tool will return a temporary file path.
6. Copy and rename the correct extracted subtitle file to match the video file name using safe_copy_and_rename_subtitle.

Custom Instructions from User: {args.instructions}

Important: Work through the files systematically.
"""
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[*genai_tools, types.Tool(function_declarations=local_tools)],
            temperature=0.0,
        )

        chat = client.chats.create(model=selected_model, config=config)

        print("Agent loop starting...")
        response = chat.send_message(
            "Please begin finding and downloading subtitles for the target directory."
        )

        MAX_TURNS = 20
        for _ in range(MAX_TURNS):
            if response.function_calls:
                parts = []
                for call in response.function_calls:
                    print(f"Agent wants to call: {call.name} with args: {call.args}")

                    if call.name in all_callables:
                        func = all_callables[call.name]
                        try:
                            kwargs = call.args if call.args else {}
                            if asyncio.iscoroutinefunction(func):
                                result = await func(**kwargs)
                            else:
                                result = func(**kwargs)
                        except Exception as e:
                            print(f"Tool error: {e}")
                            result = f"Error: {e}"

                        parts.append(
                            types.Part.from_function_response(
                                name=call.name, response={"result": str(result)}
                            )
                        )
                    else:
                        print(f"Unknown tool requested: {call.name}")
                        parts.append(
                            types.Part.from_function_response(
                                name=call.name, response={"error": "Tool not found"}
                            )
                        )
                print("Sending tool results to Agent...")
                response = chat.send_message(parts)
            else:
                print("Agent says:")
                print(response.text)
                break


if __name__ == "__main__":
    asyncio.run(main())

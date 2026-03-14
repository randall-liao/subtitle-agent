# pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType, reportUnknownParameterType, reportDeprecated, reportArgumentType, reportAny]
import argparse
import asyncio
import os
from pathlib import Path

from google import genai
from google.genai import types

import subtitle_agent.tools as tools


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
        return tools.find_video_files(str(start_dir), extensions)

    def safe_copy_and_rename_subtitle_tool(src_path: str, new_name: str):
        """Safely copies a downloaded subtitle to the target directory with its new video-matching name."""
        return tools.safe_copy_and_rename_subtitle(
            src_path, str(start_dir), new_name, str(start_dir)
        )

    def search_subtitles_tool(
        query: str | None = None,
        imdb_id: str | None = None,
        file_hash: str | None = None,
        languages: str = "en",
    ):
        """Search for subtitles on OpenSubtitles REST API."""
        return tools.search_subtitles(
            query=query, imdb_id=imdb_id, file_hash=file_hash, languages=languages
        )

    def download_subtitle_tool(file_id: str):
        """Download a subtitle from OpenSubtitles by file_id."""
        return tools.download_subtitle(file_id)

    def calculate_file_hash_tool(file_path: str):
        """Calculate the hash of a file for OpenSubtitles API."""
        return tools.calculate_file_hash(file_path)

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
        types.FunctionDeclaration(
            name="search_subtitles",
            description="Search for subtitles on OpenSubtitles REST API. Use query, imdb_id, or file_hash to search. Pass languages to filter results.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(
                        type=types.Type.STRING,
                        description="Search query (movie/show name)",
                    ),
                    "imdb_id": types.Schema(
                        type=types.Type.STRING,
                        description="IMDB ID (e.g., 'tt1234567')",
                    ),
                    "file_hash": types.Schema(
                        type=types.Type.STRING,
                        description="File hash for hash-based search",
                    ),
                    "languages": types.Schema(
                        type=types.Type.STRING,
                        description="Language code (e.g., 'en', 'zh')",
                    ),
                },
                required=[],
            ),
        ),
        types.FunctionDeclaration(
            name="download_subtitle",
            description="Download a subtitle from OpenSubtitles by file_id returned from search_subtitles.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "file_id": types.Schema(
                        type=types.Type.STRING,
                        description="The file ID from search_subtitles results",
                    )
                },
                required=["file_id"],
            ),
        ),
        types.FunctionDeclaration(
            name="calculate_file_hash",
            description="Calculate the hash of a video file for OpenSubtitles API hash-based search.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "file_path": types.Schema(
                        type=types.Type.STRING,
                        description="Absolute path to the video file",
                    )
                },
                required=["file_path"],
            ),
        ),
    ]

    all_callables = {
        "list_media_files_tool": list_media_files_tool,
        "safe_copy_and_rename_subtitle": safe_copy_and_rename_subtitle_tool,
        "search_subtitles": search_subtitles_tool,
        "download_subtitle": download_subtitle_tool,
        "calculate_file_hash": calculate_file_hash_tool,
    }

    system_instruction = f"""You are a Subtitle Agent using OpenSubtitles REST API.
Your tasks are:
1. Formulate a list of common video file extensions and pass them to list_media_files_tool to find videos missing subtitles.
2. For each media file, determine the best movie/TV show search query.
3. Use the 'search_subtitles' tool to find subtitles. Pass 'languages': '{args.language}'.
   You can search by 'query', 'imdb_id', or calculate file hash using 'calculate_file_hash'.
4. Download the best match using the 'download_subtitle' tool with the 'file_id' from the results.
5. Copy and rename the downloaded subtitle to match the video file name using safe_copy_and_rename_subtitle.

Custom Instructions from User: {args.instructions}

Important: Work through the files systematically.
"""
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[types.Tool(function_declarations=local_tools)],
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

                        print(f"Tool result: {result}")
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

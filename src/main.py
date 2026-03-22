import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.genai.types import GenerateContentConfig
from loguru import logger

from agent.prompt_logic import SYSTEM_PROMPT, get_agent_tools, initialize_agent
from core.discovery import find_videos_missing_subtitles

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Subtitle Agent (ADK Edition)")
    parser.add_argument("folder", help="Directory to scan for missing subtitles")
    parser.add_argument(
        "--model",
        default=os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite-preview"),
        help="Gemini model to use",
    )
    parser.add_argument(
        "--language",
        required=True,
        help="Natural language for the subtitles (e.g., English, French, Spanish)",
    )
    args = parser.parse_args()

    root_dir = Path(args.folder).resolve()
    if not root_dir.is_dir():
        logger.error(f"{root_dir} is not a valid directory.")
        sys.exit(1)

    logger.info(f"Scanning directory: {root_dir}")
    total_videos, videos_missing_subs = find_videos_missing_subtitles(root_dir)

    try:
        client = initialize_agent()
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        sys.exit(1)

    tools = get_agent_tools()

    logger.info(
        f"Found {total_videos} videos. {len(videos_missing_subs)} missing subtitles."
    )

    success_count = 0
    failure_count = 0

    config = GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=tools,
        temperature=0.0,
    )

    for video in videos_missing_subs:
        logger.info(f"Processing: {video.name}")
        chat = client.chats.create(model=args.model, config=config)
        prompt = (
            f"Please find and download the best subtitle for the video file: {video.name}\n"
            f"The target language requested by the user is: {args.language}\n"
            f"The original video is located at: {video.absolute()}\n"
            f"The safe base directory is: {root_dir}"
        )
        try:
            # For google-genai, providing `tools` in the Chat config automatically manages tool calls!
            chat.send_message(prompt)
            logger.debug(f"Agent finished processing {video.name}.")
            # Verify if subtitle was added
            found = False
            for ext in [".srt", ".ass", ".ssa", ".vtt"]:
                if (video.parent / f"{video.stem}{ext}").exists():
                    found = True
                    break

            if found:
                success_count += 1
                logger.success(f"Subtitle added for {video.name}")
            else:
                failure_count += 1
                logger.warning(
                    f"No subtitle found for {video.name} after agent execution."
                )

        except Exception as e:
            logger.error(f"Error processing {video.name}: {e}")
            failure_count += 1

    logger.info("Summary Report")
    logger.info(f"Total videos scanned: {total_videos}")
    logger.info(f"Subtitles successfully added: {success_count}")
    logger.info(f"Videos still missing subtitles: {failure_count}")


if __name__ == "__main__":
    main()

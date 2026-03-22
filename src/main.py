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

    batch_size = 5
    for i in range(0, len(videos_missing_subs), batch_size):
        batch = videos_missing_subs[i : i + batch_size]
        video_list_str = "\n".join([f"- {v.absolute()}" for v in batch])
        logger.info(f"Processing batch of {len(batch)} videos.")

        chat = client.chats.create(model=args.model, config=config)
        prompt = (
            f"Please process the following {len(batch)} video files and find/download/copy subtitles for them in this session:\n"
            f"{video_list_str}\n\n"
            f"The target language requested by the user is: {args.language}\n"
            f"The safe base directory is: {root_dir}"
        )

        try:
            response = chat.send_message(prompt)
            logger.debug("Agent finished processing batch.")
            logger.trace(f"Agent response: {response.text}")
        except Exception as e:
            logger.error(f"Error processing batch: {e}")

        # Verify if subtitle was added for each video in batch
        for video in batch:
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

    logger.info("Summary Report")
    logger.info(f"Total videos scanned: {total_videos}")
    logger.info(f"Subtitles successfully added: {success_count}")
    logger.info(f"Videos still missing subtitles: {failure_count}")


if __name__ == "__main__":
    main()

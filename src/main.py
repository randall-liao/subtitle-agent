import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types
from loguru import logger

from agent.prompt_logic import get_root_agent
from core.discovery import find_videos_missing_subtitles

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Subtitle Agent (ADK Edition)")
    parser.add_argument("folder", help="Directory to scan for missing subtitles")
    parser.add_argument(
        "--model",
        default=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
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

    logger.info(
        f"Found {total_videos} videos. {len(videos_missing_subs)} missing subtitles."
    )

    if not videos_missing_subs:
        logger.info("All videos already have subtitles. Nothing to do.")
        return

    # Create the ADK agent and runner
    try:
        agent = get_root_agent(model=args.model)
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        sys.exit(1)

    runner = InMemoryRunner(agent=agent, app_name="subtitle_agent")

    video_list_str = "\n".join([f"- {v.absolute()}" for v in videos_missing_subs])
    prompt = (
        f"Please process the following {len(videos_missing_subs)} video files "
        f"and find/download/copy subtitles for them:\n"
        f"{video_list_str}\n\n"
        f"The target language requested by the user is: {args.language}\n"
        f"The safe base directory is: {root_dir}"
    )

    user_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)],
    )

    logger.info("Initializing autonomous agent execution loop...")

    success_count = 0
    failure_count = 0

    try:
        for event in runner.run(
            user_id="cli_user",
            session_id="session_001",
            new_message=user_message,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_text = "\n".join(p.text for p in event.content.parts if p.text)
                logger.debug(f"Agent final response:\n{final_text}")

        logger.debug("Agent finished processing all videos.")
    except Exception as e:
        logger.error(f"Error during autonomous agent execution: {e}")

    # Verify if subtitle was added for each video
    for video in videos_missing_subs:
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
            logger.warning(f"No subtitle found for {video.name} after agent execution.")

    logger.info("Summary Report")
    logger.info(f"Total videos scanned: {total_videos}")
    logger.info(f"Subtitles successfully added: {success_count}")
    logger.info(f"Videos still missing subtitles: {failure_count}")


if __name__ == "__main__":
    main()

import json
import os
import sys

import requests
from dotenv import load_dotenv
from google import genai
from loguru import logger

# Add src to sys.path so we can import cli modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from cli.subdl_cli import search_subtitles

# from cli import tmdb_cli

# Load environment variables from .env
load_dotenv()


def check_subdl():
    logger.info("Testing SubDL API connectivity...")
    api_key = os.getenv("SUBDL_API_KEY")
    if not api_key:
        logger.error("[-] SUBDL_API_KEY is not set in .env")
        return False

    try:
        # Simple search for testing
        result = search_subtitles(api_key, film_name="Inception", type="movie")

        if result and isinstance(result, dict) and result.get("status") is True:
            logger.success("[+] SubDL API connectivity Successful!")
            logger.info(
                f"SubDL Response snippet: {json.dumps(result, indent=2)[:500]}...\n"
            )
            return True
        else:
            logger.error(f"[-] SubDL API error: {result}")
            return False

    except Exception as e:
        logger.error(f"[-] SubDL connectivity failed with exception: {e}")
        return False


def check_tmdb():
    logger.info("Testing TMDB API connectivity...")
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        logger.error("[-] TMDB_API_KEY is not set in .env")
        return False

    headers = {"accept": "application/json", "Authorization": f"Bearer {api_key}"}

    try:
        url = "https://api.themoviedb.org/3/movie/27205?language=en-US"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        if result and isinstance(result, dict) and "title" in result:
            logger.success("[+] TMDB API connectivity Successful!")
            logger.info(
                f"TMDB Response snippet: {json.dumps(result, indent=2)[:500]}...\n"
            )
            return True
        else:
            logger.error(f"[-] TMDB API error: {result}")
            return False
    except requests.exceptions.HTTPError as e:
        logger.error(f"[-] TMDB connectivity failed HTTPError: {e}")
        return False
    except Exception as e:
        logger.error(f"[-] TMDB connectivity failed with exception: {e}")
        return False


def check_gemini():
    logger.info("Testing Gemini API connectivity...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("[-] GEMINI_API_KEY is not set in .env")
        return False

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview"),
            contents="Say 'hello world'",
        )
        if response.text:
            logger.success(
                f"[+] Gemini API connectivity Successful! Response: {response.text.strip()}\n"
            )
            return True
        else:
            logger.error("[-] Gemini API error: Empty response")
            return False
    except Exception as e:
        logger.error(f"[-] Gemini connectivity failed with exception: {e}")
        return False


if __name__ == "__main__":
    logger.info("--- Running E2E Connectivity Tests ---")
    subdl_ok = check_subdl()
    tmdb_ok = check_tmdb()
    gemini_ok = check_gemini()

    if all([subdl_ok, tmdb_ok, gemini_ok]):
        logger.success("All connectivity tests passed.")
        sys.exit(0)
    else:
        logger.error("Some connectivity tests failed.")
        sys.exit(1)

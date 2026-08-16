"""llm.py — the ONLY file that talks to Gemini.

Everything else calls ask() (free text) or ask_json() (structured
JSON). Both retry on transient API errors (503 high demand / 429
rate limit) before giving up honestly."""
import json
import time

from google import genai
from google.genai import types
import config

# One-time setup: log in with our key
client = genai.Client(api_key=config.GEMINI_API_KEY)


def ask(prompt, retries=3):
    """Send a prompt to Gemini, return the reply text.
    Retries on transient errors (503 'high demand') before giving up."""
    for attempt in range(retries):
        try:
            return client.models.generate_content(
                model=config.MODEL_NAME, contents=prompt
            ).text
        except Exception:
            if attempt == retries - 1:   # out of retries -> fail honestly
                raise
            time.sleep(2)                # brief pause, then try again


def ask_json(prompt, retries=3):
    """Ask Gemini to return JSON; the Google API enforces valid JSON."""
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=config.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            return json.loads(response.text)
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2)
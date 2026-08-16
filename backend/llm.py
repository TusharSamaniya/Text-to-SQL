# llm.py — the ONLY file that talks to Gemini.
# Everything else calls ask() and gets text back.
import time

from google import genai
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
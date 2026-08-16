# llm.py — the ONLY file that talks to Gemini.
# Everything else calls ask() and gets text back.
from google import genai
import config

# One-time setup: log in with our key
client = genai.Client(api_key=config.GEMINI_API_KEY)


def ask(prompt):
    """Send a prompt to Gemini, return the reply text."""
    return client.models.generate_content(
        model=config.MODEL_NAME, contents=prompt
    ).text
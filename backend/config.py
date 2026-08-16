import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("Missing DATABASE_URL in .env")

# Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
if not GEMINI_API_KEY:
    raise SystemExit("Missing GEMINI_API_KEY in .env")
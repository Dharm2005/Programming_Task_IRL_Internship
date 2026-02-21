import os
from dotenv import load_dotenv
from pathlib import Path


# Force load .env from root folder
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = "models/gemini-1.5-flash"
    MAX_HISTORY = 10

import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

class Settings:
    PROJECT_NAME: str = "AI-Powered Real-Time ICU Monitoring Dashboard"
    # Loads from .env, defaults to SQLite for simple local dev
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./icu_vitals.db")

settings = Settings()

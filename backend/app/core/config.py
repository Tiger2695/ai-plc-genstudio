import os
from pathlib import Path
from dotenv import load_dotenv


# Base Directory path setup (.env tak pahunchne ke liye)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"

# .env file ko load karna
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = os.getenv("APP_NAME", "AI PLC Assistant")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # ⚡ LLM Model Engine Configurations (2026 Production Standards)
    # Agar model change karna ho toh pure project me sirf yahan badalna padega
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash-lite")

    def validate_keys(self):
        """Industrial check to ensure infrastructure won't crash at runtime"""
        if not self.GEMINI_API_KEY and not self.OPENAI_API_KEY:
            raise ValueError("🚨 CRITICAL CRASH: Dono Gemini aur OpenAI keys missing hain .env file mein!")

# Single instance initialize karna poore application ke liye
settings = Settings()
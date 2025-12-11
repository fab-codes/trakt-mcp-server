from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

class AppConfig:
    TRAKT_CLIENT_ID = os.getenv("TRAKT_CLIENT_ID")
    TRAKT_CLIENT_SECRET = os.getenv("TRAKT_CLIENT_SECRET")
    PROJECT_ROOT = Path(__file__).parent.parent
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def validate_config():
    missing = []
    if not AppConfig.TRAKT_CLIENT_ID:
        missing.append("TRAKT_CLIENT_ID")
    if not AppConfig.TRAKT_CLIENT_SECRET:
        missing.append("TRAKT_CLIENT_SECRET")
    
    if missing:
        raise ValueError(f"Missing environment variables: {missing}")
    
validate_config()
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/ai_saas.db")

# App settings
APP_ENV = os.getenv("APP_ENV", "development")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Scraper settings
SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "24"))
MAX_TOOLS_PER_RUN = int(os.getenv("MAX_TOOLS_PER_RUN", "100"))

print(f"[Config] Environment: {APP_ENV}")
print(f"[Config] Groq API: {'SET' if GROQ_API_KEY else 'NOT SET'}")
print(f"[Config] Gemini API: {'SET' if GEMINI_API_KEY else 'NOT SET'}")

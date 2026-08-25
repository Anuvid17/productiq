from dotenv import load_dotenv
import os

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

MODEL_NAME = os.getenv("MODEL_NAME", "llama3.1")

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

TEMPERATURE = float(
    os.getenv("TEMPERATURE", "0.2")
)

MAX_RETRIES = int(
    os.getenv("MAX_RETRIES", "2")
)

OLLAMA_TIMEOUT = float(
    os.getenv("OLLAMA_TIMEOUT", "120.0")
)

raw_db_url = os.getenv("DATABASE_URL", "").strip()

if not raw_db_url or "localhost" in raw_db_url or "127.0.0.1" in raw_db_url:
    DATABASE_URL = "sqlite:///productiq_dev.db"
elif raw_db_url.startswith("postgres://"):
    DATABASE_URL = raw_db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif raw_db_url.startswith("postgresql://") and "+psycopg" not in raw_db_url:
    DATABASE_URL = raw_db_url.replace("postgresql://", "postgresql+psycopg://", 1)
else:
    DATABASE_URL = raw_db_url

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO"
)

raw_cors = os.getenv(
    "CORS_ORIGINS",
    "*,http://localhost:5173,http://127.0.0.1:5173,https://productiq-frontend.onrender.com"
)
CORS_ORIGINS = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]
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

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/productiq"
)

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO"
)

raw_cors = os.getenv(
    "CORS_ORIGINS",
    "*,http://localhost:5173,http://127.0.0.1:5173,https://productiq-frontend.onrender.com"
)
CORS_ORIGINS = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]
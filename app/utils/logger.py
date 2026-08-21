import sys
from pathlib import Path
from loguru import logger

# Ensure log directory exists
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "productiq.log"

# Configure single central loguru instance
logger.remove()

# File Handler
logger.add(
    str(LOG_FILE),
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    enqueue=True,
    backtrace=True,
    diagnose=True
)

# Console Handler
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)


__all__ = ["logger"]
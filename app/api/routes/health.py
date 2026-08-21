from fastapi import APIRouter
from app.database.db import check_db_health
from app.llm.ollama_client import OllamaClient

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health() -> dict:
    """
    Health check endpoint returning ProductIQ service, database, and Ollama status.
    Does not crash if PostgreSQL or Ollama is offline.
    """
    db_health = check_db_health()
    ollama_client = OllamaClient()
    ollama_health = ollama_client.check_health()

    return {
        "status": "ok",
        "service": "ProductIQ",
        "database": db_health,
        "ollama": ollama_health
    }

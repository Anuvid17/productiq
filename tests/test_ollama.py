import pytest
import urllib.request
from app.llm.ollama_client import OllamaClient
from app.config import OLLAMA_HOST


def is_ollama_available() -> bool:
    try:
        url = f"{OLLAMA_HOST.rstrip('/')}/api/tags"
        with urllib.request.urlopen(url, timeout=2.0) as resp:
            return resp.status == 200
    except Exception:
        return False


@pytest.mark.skipif(not is_ollama_available(), reason="Ollama server is unavailable")
def test_ollama_generate():
    client = OllamaClient()
    response = client.generate("Reply with exact word: PONG")
    assert isinstance(response, str)
    assert len(response.strip()) > 0


if __name__ == "__main__":
    if is_ollama_available():
        client = OllamaClient()
        res = client.generate("What is Deep Learning?")
        print("\nOllama Response Received:")
        print(res)
    else:
        print(f"\nOllama server is not available at {OLLAMA_HOST}.")
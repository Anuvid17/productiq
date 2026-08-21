import time
from typing import Optional
from ollama import Client as SyncOllamaClient
from app.utils.logger import logger
from app.config import (
    MODEL_NAME,
    OLLAMA_HOST,
    TEMPERATURE,
    MAX_RETRIES,
    OLLAMA_TIMEOUT
)


class OllamaClient:
    """
    Synchronous client wrapper for local Ollama LLM execution.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        host: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None
    ):
        self.model = model or MODEL_NAME
        self.host = host or OLLAMA_HOST
        self.timeout = timeout or OLLAMA_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else MAX_RETRIES
        self._client = SyncOllamaClient(host=self.host, timeout=self.timeout)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text response from Ollama model.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"Ollama prompt execution attempt {attempt + 1}/{self.max_retries} [Model: {self.model}]"
                )
                start = time.time()
                response = self._client.chat(
                    model=self.model,
                    messages=messages,
                    options={"temperature": TEMPERATURE}
                )
                end = time.time()
                duration = end - start
                logger.info(f"Ollama generation completed in {duration:.2f}s")
                return response.message.content
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Ollama generation attempt {attempt + 1} encountered error: {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(0.5)

        logger.error(
            f"Ollama generation failed after {self.max_retries} attempts."
        )
        raise RuntimeError(
            f"Failed to generate response from Ollama ({self.model}): {last_error}"
        ) from last_error

    def check_health(self) -> dict:
        """
        Lightweight health check inspecting local Ollama server connectivity.
        """
        import urllib.request
        url = f"{self.host.rstrip('/')}/api/tags"
        try:
            with urllib.request.urlopen(url, timeout=2.0) as resp:
                is_ok = resp.status == 200
                return {
                    "available": is_ok,
                    "model": self.model
                }
        except Exception as e:
            return {
                "available": False,
                "model": self.model,
                "error": str(e)
            }
from pathlib import Path

class PromptLoader:

    @staticmethod
    def load(path: str):
        file = Path(path)
        if not file.exists():
            raise FileNotFoundError(path)
        return file.read_text(
            encoding="utf-8"
        )
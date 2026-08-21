import json

class JSONParser:

    @staticmethod
    def parse(response: str):
        cleaned = (
            response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            return json.loads(cleaned)
        except Exception as e:
            raise ValueError(
                f"Invalid JSON Returned\n\n{cleaned}"
            ) from e
from pydantic import BaseModel


def make_json_prompt(example: BaseModel) -> str:
    return f"Respond in JSON format like `{example.model_dump_json()}`."

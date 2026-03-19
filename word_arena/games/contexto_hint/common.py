from pathlib import Path

from pydantic import BaseModel


class ContextoHintConfig(BaseModel):
    data_file: Path
    num_candidates: int
    game_id: int


class ContextoHintGuess(BaseModel):
    index: int


class ContextoHintFeedback(BaseModel):
    distance: int
    next_choices: list[str] | None

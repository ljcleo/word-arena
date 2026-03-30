from pathlib import Path

from pydantic import BaseModel


class NumberleConfig(BaseModel):
    data_file: Path
    eq_pool: dict[int, str]
    eq_length: int
    max_turns: int
    game_ids: list[int]


class NumberleInfo(BaseModel):
    num_targets: int
    eq_length: int
    max_turns: int


class NumberleGuess(BaseModel):
    equation: str


type NumberleFeedback = list[str] | bool


class NumberleFinalResult(BaseModel):
    found_indices: set[int]
    answers: list[str]

from pydantic import BaseModel
from pathlib import Path


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


class NumberleResponse(BaseModel):
    patterns: list[str]


class NumberleError(BaseModel):
    error: str


type NumberleFeedback = NumberleResponse | NumberleError


class NumberleFinalResult(BaseModel):
    found_indices: set[int]
    answers: list[str]

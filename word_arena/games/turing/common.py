from pathlib import Path

from pydantic import BaseModel


class TuringConfig(BaseModel):
    data_file: Path
    card_pool: dict[int, list[str]]
    num_verifiers: int
    max_turns: int
    game_id: int


class TuringInfo(BaseModel):
    verifiers: list[list[str]]
    max_turns: int


class TuringGuess(BaseModel):
    code: int
    verifiers: list[int]


type TuringFeedback = list[bool] | bool | str


class TuringFinalResult(BaseModel):
    verdict: bool | None
    num_questions: int
    answer: int

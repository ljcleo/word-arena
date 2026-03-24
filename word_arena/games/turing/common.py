from enum import StrEnum, auto, unique
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


@unique
class TuringError(StrEnum):
    INVALID_CODE = auto()
    TOO_MANY_VERIFIERS = auto()
    INVALID_VERIFIER = auto()


type TuringFeedback = list[bool] | bool | TuringError


class TuringFinalResult(BaseModel):
    verdict: bool | None
    num_questions: int
    answer: int

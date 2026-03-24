from enum import unique, auto, StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, WithJsonSchema


class StrandsConfig(BaseModel):
    data_file: Path
    max_turns: int
    game_id: int


class StrandsInfo(BaseModel):
    board: list[str]
    clue: str
    max_turns: int


class StrandsGuess(BaseModel):
    coords: list[
        Annotated[
            tuple[int, int],
            WithJsonSchema(
                {"items": {"type": "integer"}, "maxItems": 2, "minItems": 2, "type": "array"}
            ),
        ]
    ]


@unique
class StrandsError(StrEnum):
    EMPTY = auto()
    OUT_OF_BOUNDS = auto()
    NOT_CONTINUOUS = auto()
    OVERLAP = auto()
    USED = auto()


type StrandsFeedback = int | StrandsError


class StrandsFinalResult(BaseModel):
    found_indices: set[int]
    answers: list[tuple[str, list[tuple[int, int]]]]

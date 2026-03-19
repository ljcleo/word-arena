from typing import Annotated

from pydantic import BaseModel, WithJsonSchema


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


type StrandsFeedback = str | int


class StrandsFinalResult(BaseModel):
    found_indices: set[int]
    answers: list[tuple[str, list[tuple[int, int]]]]

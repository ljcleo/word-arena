from pathlib import Path

from pydantic import BaseModel


class ConexoConfig(BaseModel):
    data_file: Path
    max_turns: int
    game_id: int


class ConexoInfo(BaseModel):
    words: list[str]
    group_size: int
    max_turns: int


class ConexoGuess(BaseModel):
    indices: list[int]


class ConexoFeedback(BaseModel):
    accepted: bool
    message: str | None


class ConexoWordGroup(BaseModel):
    theme: str
    words: list[str]


class ConexoFinalResult(BaseModel):
    found_groups: list[ConexoWordGroup]
    remaining_groups: list[ConexoWordGroup]

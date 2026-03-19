from pathlib import Path

from pydantic import BaseModel


class ConnectionsConfig(BaseModel):
    data_file: Path
    max_turns: int
    game_id: int


class ConnectionsInfo(BaseModel):
    words: list[str]
    group_size: int
    max_turns: int


class ConnectionsGuess(BaseModel):
    indices: list[int]


class ConnectionsFeedback(BaseModel):
    accepted: bool
    message: str | None


class ConnectionsWordGroup(BaseModel):
    theme: str
    words: list[str]


class ConnectionsFinalResult(BaseModel):
    found_groups: list[ConnectionsWordGroup]
    remaining_groups: list[ConnectionsWordGroup]

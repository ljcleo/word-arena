from pydantic import BaseModel


class ConnectionsInfo(BaseModel):
    words: list[str]
    group_size: int
    max_guesses: int


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


class ConnectionsNote(BaseModel):
    law: str
    strategy: str

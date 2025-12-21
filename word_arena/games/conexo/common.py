from pydantic import BaseModel


class ConexoInfo(BaseModel):
    words: list[str]
    group_size: int
    max_guesses: int


class ConexoFeedback(BaseModel):
    accepted: bool
    message: str | None


class ConexoWordGroup(BaseModel):
    theme: str
    words: list[str]


class ConexoFinalResult(BaseModel):
    found_groups: list[ConexoWordGroup]
    remaining_groups: list[ConexoWordGroup]


class ConexoExperience(BaseModel):
    law: str
    strategy: str

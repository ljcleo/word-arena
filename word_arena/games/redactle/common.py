from pathlib import Path

from pydantic import BaseModel


class RedactleConfig(BaseModel):
    data_file: Path
    stop_words: set[str]
    game_id: int
    max_turns: int


class RedactleInfo(BaseModel):
    article: list[list[tuple[str, str | None]]]
    stop_words: set[str]
    max_turns: int


class RedactleGuess(BaseModel):
    word: str


class RedactleResponse(BaseModel):
    word: str
    lemma: str
    positions: list[tuple[int, int]]


class RedactleError(BaseModel):
    error: str


type RedactleFeedback = RedactleResponse | RedactleError


class RedactleFinalResult(BaseModel):
    found_words: set[str]
    title: str
    title_words: set[str]

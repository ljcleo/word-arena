from pydantic import BaseModel


class ContextoGuess(BaseModel):
    word: str


class ContextoResponse(BaseModel):
    word: str
    lemma: str
    distance: int


class ContextoError(BaseModel):
    error: str


type ContextoFeedback = ContextoResponse | ContextoError


class ContextoFinalResult(BaseModel):
    best_pos: int
    best_word: str
    top_words: list[str]


class ContextoNote(BaseModel):
    law: str
    strategy: str

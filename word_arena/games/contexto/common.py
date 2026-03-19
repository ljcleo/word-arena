from pydantic import BaseModel


class ContextoConfig(BaseModel):
    max_turns: int
    game_id: int


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

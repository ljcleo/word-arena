from pydantic import BaseModel


class LetrosoInfo(BaseModel):
    num_targets: int
    max_letters: int
    max_guesses: int


class LetrosoGuess(BaseModel):
    word: str


class LetrosoResponse(BaseModel):
    patterns: list[str]


class LetrosoError(BaseModel):
    error: str


type LetrosoFeedback = LetrosoResponse | LetrosoError


class LetrosoFinalResult(BaseModel):
    found_indices: set[int]
    answers: list[str]


class LetrosoExperience(BaseModel):
    strategy: str

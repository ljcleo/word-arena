from pydantic import BaseModel


class NumberleInfo(BaseModel):
    num_targets: int
    expr_len: int
    max_guesses: int


class NumberleGuess(BaseModel):
    equation: str


class NumberleResponse(BaseModel):
    patterns: list[str]


class NumberleError(BaseModel):
    error: str


type NumberleFeedback = NumberleResponse | NumberleError


class NumberleFinalResult(BaseModel):
    found_indices: set[int]
    answers: list[str]


class NumberleExperience(BaseModel):
    strategy: str

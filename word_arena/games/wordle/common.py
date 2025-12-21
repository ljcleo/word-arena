from pydantic import BaseModel


class WordleInfo(BaseModel):
    num_targets: int
    max_guesses: int


class WordleResponse(BaseModel):
    patterns: list[str]


class WordleError(BaseModel):
    error: str


type WordleFeedback = WordleResponse | WordleError


class WordleFinalResult(BaseModel):
    found_indices: set[int]
    answers: list[str]


class WordleExperience(BaseModel):
    strategy: str

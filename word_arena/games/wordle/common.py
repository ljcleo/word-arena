from pydantic import BaseModel


class WordleConfig(BaseModel):
    word_pool: dict[int, str]
    max_turns: int
    game_ids: list[int]


class WordleInfo(BaseModel):
    num_targets: int
    max_turns: int


class WordleGuess(BaseModel):
    word: str


type WordleFeedback = list[str] | bool


class WordleFinalResult(BaseModel):
    found_indices: set[int]
    answers: list[str]

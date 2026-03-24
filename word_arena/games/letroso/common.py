from pydantic import BaseModel


class LetrosoConfig(BaseModel):
    word_pool: dict[int, str]
    max_letters: int
    max_turns: int
    game_ids: list[int]


class LetrosoInfo(BaseModel):
    num_targets: int
    max_letters: int
    max_turns: int


class LetrosoGuess(BaseModel):
    word: str


type LetrosoFeedback = list[str] | bool


class LetrosoFinalResult(BaseModel):
    found_indices: set[int]
    answers: list[str]

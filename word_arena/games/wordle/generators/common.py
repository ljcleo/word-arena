from pydantic import BaseModel


class WordleSetting(BaseModel):
    num_targets: int
    max_guesses: int


class WordleConfig(BaseModel):
    word_list: list[str]
    target_ids: list[int]
    max_guesses: int

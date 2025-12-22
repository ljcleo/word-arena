from pydantic import BaseModel


class LetrosoSetting(BaseModel):
    num_targets: int
    max_letters: int
    max_guesses: int


class LetrosoConfig(BaseModel):
    word_list: list[str]
    target_ids: list[int]
    max_letters: int
    max_guesses: int

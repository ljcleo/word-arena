from pydantic import BaseModel


class WordleMetaConfig(BaseModel):
    word_list: list[str]
    target_pool: list[int]


class WordleMutableMetaConfig(BaseModel):
    max_guesses: int
    num_targets: int


class WordleConfig(BaseModel):
    max_guesses: int
    game_ids: list[int]

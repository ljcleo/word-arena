from pydantic import BaseModel


class WordleMetaConfig(BaseModel):
    word_list: list[str]
    target_pool: list[int]

    @property
    def game_count(self) -> int:
        return len(self.target_pool)


class WordleMutableMetaConfig(BaseModel):
    max_guesses: int
    num_targets: int


class WordleConfig(BaseModel):
    max_guesses: int
    game_ids: list[int]

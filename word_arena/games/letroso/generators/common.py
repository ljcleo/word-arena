from pydantic import BaseModel


class LetrosoMetaConfig(BaseModel):
    word_list: list[str]
    target_pool: list[int]

    @property
    def game_count(self) -> int:
        return len(self.target_pool)


class LetrosoMutableMetaConfig(BaseModel):
    max_letters: int
    max_guesses: int
    num_targets: int


class LetrosoConfig(BaseModel):
    max_letters: int
    max_guesses: int
    game_ids: list[int]

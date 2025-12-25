from pydantic import BaseModel


class NumberleMetaConfig(BaseModel):
    eq_list: list[str]
    target_pool: dict[int, list[int]]

    def get_game_count(self, *, eq_length: int) -> int:
        return len(self.target_pool[eq_length])


class NumberleMutableMetaConfig(BaseModel):
    eq_length: int
    max_guesses: int
    num_targets: int


class NumberleConfig(BaseModel):
    eq_length: int
    max_guesses: int
    game_ids: list[int]

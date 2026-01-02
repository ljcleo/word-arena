from collections.abc import Callable
from datetime import date
from random import Random

from pydantic import BaseModel


def get_contexto_game_count() -> int:
    return (date.today() - date(2022, 9, 18)).days + 1


def select_game_id(*, selector: Callable[[int], int]) -> int:
    return selector(get_contexto_game_count())


def random_game_id(*, rng: Random) -> int:
    return rng.randrange(get_contexto_game_count())


class ContextoConfig(BaseModel):
    max_guesses: int
    game_id: int

from datetime import date

from pydantic import BaseModel


def get_contexto_game_count() -> int:
    return (date.today() - date(2022, 9, 18)).days + 1


class ContextoConfig(BaseModel):
    max_guesses: int
    game_id: int

from pydantic import BaseModel


class ContextoConfig(BaseModel):
    max_guesses: int
    game_id: int

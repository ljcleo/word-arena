from pydantic import BaseModel


class ConexoConfig(BaseModel):
    max_guesses: int
    game_id: int

from pydantic import BaseModel


class ContextoSetting(BaseModel):
    max_guesses: int


class ContextoConfig(BaseModel):
    game_id: int
    max_guesses: int

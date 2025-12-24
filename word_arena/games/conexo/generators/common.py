from pydantic import BaseModel


class ConexoConfig(BaseModel):
    max_guesses: int
    game_id: int


class ConexoGroupData(BaseModel):
    indices: list[int]
    theme: str


class ConexoGameData(BaseModel):
    id: int
    words: list[str]
    groups: list[ConexoGroupData]

from pydantic import BaseModel


class ConexoSetting(BaseModel):
    max_guesses: int


class ConexoConfig(BaseModel):
    game_id: int
    max_guesses: int


class ConexoGroupData(BaseModel):
    indices: list[int]
    theme: str


class ConexoGameData(BaseModel):
    id: int
    words: list[str]
    groups: list[ConexoGroupData]

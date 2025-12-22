from pydantic import BaseModel


class ContextoHintSetting(BaseModel):
    num_candidates: int


class ContextoHintConfig(BaseModel):
    game_id: int
    num_candidates: int

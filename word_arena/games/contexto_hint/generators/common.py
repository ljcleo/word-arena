from pydantic import BaseModel


class ContextoHintConfig(BaseModel):
    num_candidates: int
    game_id: int

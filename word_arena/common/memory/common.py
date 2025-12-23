from pydantic import BaseModel

from ..game.common import GameRecord


class Analysis(BaseModel):
    analysis: str
    plan: str


class Reflection(BaseModel):
    summary: str
    reflection: str


class GameSummary[IT, HT, GT, FT, RT](BaseModel):
    game_record: GameRecord[IT, HT, GT, FT, RT]
    latest_analysis: Analysis | None
    reflection: Reflection

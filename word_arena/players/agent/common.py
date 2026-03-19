from __future__ import annotations

from pydantic import BaseModel

from ...common.game.common import Trajectory


class Analysis(BaseModel):
    analysis: str
    plan: str


class AnalyzedGuess[GT](BaseModel):
    analysis: Analysis | None
    guess: GT


class GameRecord[IT, GT, FT, RT](BaseModel):
    trajectory: Trajectory[IT, GT, FT]
    last_analysis: Analysis | None
    final_result: RT


class Reflection(BaseModel):
    summary: str
    reflection: str


class GameSummary[IT, GT, FT, RT](BaseModel):
    game_record: GameRecord[IT, GT, FT, RT]
    reflection: Reflection

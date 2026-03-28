from pydantic import BaseModel

from ...common.game.common import Trajectory


class AnalyzedGuess[AT, GT](BaseModel):
    analysis: AT | None
    guess: GT


class GameRecord[IT, AT, GT, FT, RT](BaseModel):
    trajectory: Trajectory[IT, GT, FT]
    last_analysis: AT | None
    final_result: RT


class GameSummary[IT, AT, GT, FT, RT, ST](BaseModel):
    game_record: GameRecord[IT, AT, GT, FT, RT]
    reflection: ST

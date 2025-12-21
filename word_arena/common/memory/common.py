from pydantic import BaseModel


class Analysis(BaseModel):
    past_analysis_summary: str
    current_analysis: str
    plan: str


class Turn[HT, GT, FT](BaseModel):
    hint: HT
    guess: GT
    feedback: FT


class Reflection(BaseModel):
    summary: str
    lessons: str


class GameRecord[IT, HT, GT, FT, RT](BaseModel):
    game_info: IT
    trajectory: list[Turn[HT, GT, FT]]
    latest_analysis: Analysis | None
    final_result: RT


class GameSummary[IT, HT, GT, FT, RT](BaseModel):
    record: GameRecord[IT, HT, GT, FT, RT]
    reflection: Reflection

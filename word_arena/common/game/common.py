from pydantic import BaseModel


class Turn[HT, GT, FT](BaseModel):
    hint: HT
    guess: GT
    feedback: FT


class GameRecord[IT, HT, GT, FT, RT](BaseModel):
    game_info: IT
    trajectory: list[Turn[HT, GT, FT]]
    final_result: RT

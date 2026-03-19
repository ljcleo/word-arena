from enum import Enum, auto, unique

from pydantic import BaseModel


@unique
class GameStatus(Enum):
    PRE = auto()
    IN = auto()
    POST = auto()


class GuessFeedback[FT](BaseModel):
    feedback: FT
    is_over: bool


class Turn[GT, FT](BaseModel):
    guess: GT
    feedback: FT


class Trajectory[IT, GT, FT](BaseModel):
    game_info: IT
    turns: list[Turn[GT, FT]]

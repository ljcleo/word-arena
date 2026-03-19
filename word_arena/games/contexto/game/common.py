from pydantic import BaseModel

from ....common.game.state import GameStateInterface
from ..common import ContextoFeedback, ContextoFinalResult, ContextoGuess


class ContextoConfig(BaseModel):
    max_turns: int
    game_id: int


type ContextoGameStateInterface = GameStateInterface[
    int, ContextoGuess, ContextoFeedback, ContextoFinalResult
]

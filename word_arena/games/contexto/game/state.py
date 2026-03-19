from ....common.game.state import GameStateInterface
from ..common import ContextoFeedback, ContextoFinalResult, ContextoGuess

type ContextoGameStateInterface = GameStateInterface[
    int, ContextoGuess, ContextoFeedback, ContextoFinalResult
]

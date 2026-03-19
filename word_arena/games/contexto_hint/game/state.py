from ....common.game.state import GameStateInterface
from ..common import ContextoHintFeedback, ContextoHintGuess

type ContextoHintGameStateInterface = GameStateInterface[
    list[str], ContextoHintGuess, ContextoHintFeedback, list[str]
]

from ....common.game.state import GameStateInterface
from ..common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo

type LetrosoGameStateInterface = GameStateInterface[
    LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult
]

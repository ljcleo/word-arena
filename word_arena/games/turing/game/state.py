from ....common.game.state import GameStateInterface
from ..common import TuringFeedback, TuringFinalResult, TuringGuess, TuringInfo

type TuringGameStateInterface = GameStateInterface[
    TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult
]

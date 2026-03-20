from ....common.game.state import GameStateInterface
from ..common import RedactleFeedback, RedactleFinalResult, RedactleGuess, RedactleInfo

type RedactleGameStateInterface = GameStateInterface[
    RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult
]

from ....common.game.state import GameStateInterface
from ..common import NumberleFeedback, NumberleFinalResult, NumberleGuess, NumberleInfo

type NumberleGameStateInterface = GameStateInterface[
    NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult
]

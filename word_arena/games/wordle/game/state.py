from ....common.game.state import GameStateInterface
from ..common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo

type WordleGameStateInterface = GameStateInterface[
    WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult
]

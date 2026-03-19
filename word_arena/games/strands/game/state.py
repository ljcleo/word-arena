from ....common.game.state import GameStateInterface
from ..common import StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo

type StrandsGameStateInterface = GameStateInterface[
    StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult
]

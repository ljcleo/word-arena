from ....common.game.state import GameStateInterface
from ..common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo

type ConexoGameStateInterface = GameStateInterface[
    ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult
]

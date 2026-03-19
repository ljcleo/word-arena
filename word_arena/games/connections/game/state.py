from ....common.game.state import GameStateInterface
from ..common import ConnectionsFeedback, ConnectionsFinalResult, ConnectionsGuess, ConnectionsInfo

type ConnectionsGameStateInterface = GameStateInterface[
    ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback, ConnectionsFinalResult
]

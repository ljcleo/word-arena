from pydantic import BaseModel

from .....players.agent.common import GameRecord
from .....players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ...common import ConnectionsFeedback, ConnectionsFinalResult, ConnectionsGuess, ConnectionsInfo


class ConnectionsNote(BaseModel):
    law: str
    strategy: str


type ConnectionsGameStateInterface = AgentGameStateInterface[
    ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback, ConnectionsFinalResult
]

type ConnectionsNoteStateInterface = AgentNoteStateInterface[
    ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback, ConnectionsFinalResult, ConnectionsNote
]

type ConnectionsGameRecord = GameRecord[
    ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback, ConnectionsFinalResult
]

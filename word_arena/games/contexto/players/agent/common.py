from pydantic import BaseModel

from .....players.agent.common import GameRecord
from .....players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ...common import ContextoFeedback, ContextoFinalResult, ContextoGuess


class ContextoNote(BaseModel):
    law: str
    strategy: str


type ContextoGameStateInterface = AgentGameStateInterface[
    int, ContextoGuess, ContextoFeedback, ContextoFinalResult
]

type ContextoNoteStateInterface = AgentNoteStateInterface[
    int, ContextoGuess, ContextoFeedback, ContextoFinalResult, ContextoNote
]

type ContextoGameRecord = GameRecord[int, ContextoGuess, ContextoFeedback, ContextoFinalResult]

from pydantic import BaseModel

from .....players.agent.common import GameRecord
from .....players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ...common import ContextoHintFeedback, ContextoHintGuess


class ContextoHintNote(BaseModel):
    law: str
    strategy: str


type ContextoHintGameStateInterface = AgentGameStateInterface[
    list[str], ContextoHintGuess, ContextoHintFeedback, list[str]
]

type ContextoHintNoteStateInterface = AgentNoteStateInterface[
    list[str], ContextoHintGuess, ContextoHintFeedback, list[str], ContextoHintNote
]

type ContextoHintGameRecord = GameRecord[
    list[str], ContextoHintGuess, ContextoHintFeedback, list[str]
]

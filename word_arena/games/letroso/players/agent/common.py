from pydantic import BaseModel

from .....players.agent.common import GameRecord
from .....players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ...common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo


class LetrosoNote(BaseModel):
    strategy: str


type LetrosoGameStateInterface = AgentGameStateInterface[
    LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult
]

type LetrosoNoteStateInterface = AgentNoteStateInterface[
    LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult, LetrosoNote
]

type LetrosoGameRecord = GameRecord[LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult]

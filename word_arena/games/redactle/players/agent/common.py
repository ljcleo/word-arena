from pydantic import BaseModel

from .....players.agent.common import GameRecord
from .....players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ...common import RedactleFeedback, RedactleFinalResult, RedactleGuess, RedactleInfo


class RedactleNote(BaseModel):
    strategy: str


type RedactleGameStateInterface = AgentGameStateInterface[
    RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult
]

type RedactleNoteStateInterface = AgentNoteStateInterface[
    RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult, RedactleNote
]

type RedactleGameRecord = GameRecord[
    RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult
]

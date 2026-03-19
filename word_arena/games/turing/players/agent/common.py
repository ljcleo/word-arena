from pydantic import BaseModel

from .....players.agent.common import GameRecord
from .....players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ...common import TuringFeedback, TuringFinalResult, TuringGuess, TuringInfo


class TuringNote(BaseModel):
    strategy: str


type TuringGameStateInterface = AgentGameStateInterface[
    TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult
]

type TuringNoteStateInterface = AgentNoteStateInterface[
    TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult, TuringNote
]

type TuringGameRecord = GameRecord[TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult]

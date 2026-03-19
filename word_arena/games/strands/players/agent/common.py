from pydantic import BaseModel

from .....players.agent.common import GameRecord
from .....players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ...common import StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo


class StrandsNote(BaseModel):
    strategy: str


type StrandsGameStateInterface = AgentGameStateInterface[
    StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult
]

type StrandsNoteStateInterface = AgentNoteStateInterface[
    StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult, StrandsNote
]

type StrandsGameRecord = GameRecord[StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult]

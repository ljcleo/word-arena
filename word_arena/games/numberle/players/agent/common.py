from pydantic import BaseModel

from .....players.agent.common import GameRecord
from .....players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ...common import NumberleFeedback, NumberleFinalResult, NumberleGuess, NumberleInfo


class NumberleNote(BaseModel):
    strategy: str


type NumberleGameStateInterface = AgentGameStateInterface[
    NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult
]

type NumberleNoteStateInterface = AgentNoteStateInterface[
    NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult, NumberleNote
]

type NumberleGameRecord = GameRecord[
    NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult
]

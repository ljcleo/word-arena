from pydantic import BaseModel

from .....players.agent.common import GameRecord
from .....players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ...common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo


class WordleNote(BaseModel):
    strategy: str


type WordleGameStateInterface = AgentGameStateInterface[
    WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult
]

type WordleNoteStateInterface = AgentNoteStateInterface[
    WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult, WordleNote
]

type WordleGameRecord = GameRecord[WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult]

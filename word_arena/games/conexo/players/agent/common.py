from pydantic import BaseModel

from .....players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from .....players.agent.common import GameRecord
from ...common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo


class ConexoNote(BaseModel):
    law: str
    strategy: str


type ConexoGameStateInterface = AgentGameStateInterface[
    ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult
]

type ConexoNoteStateInterface = AgentNoteStateInterface[
    ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult, ConexoNote
]

type ConexoGameRecord = GameRecord[ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult]

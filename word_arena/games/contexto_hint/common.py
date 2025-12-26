from pydantic import BaseModel


class ContextoHintGuess(BaseModel):
    index: int


class ContextoHintNote(BaseModel):
    law: str
    strategy: str

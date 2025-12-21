from pydantic import BaseModel


class ContextoHintGuess(BaseModel):
    index: int


class ContextoHintExperience(BaseModel):
    law: str
    strategy: str

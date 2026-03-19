from pydantic import BaseModel


class ContextoHintGuess(BaseModel):
    index: int


class ContextoHintFeedback(BaseModel):
    distance: int
    next_choices: list[str] | None

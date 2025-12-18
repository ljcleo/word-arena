from pydantic import BaseModel


class LetrosoInfo(BaseModel):
    num_targets: int
    max_letters: int
    max_guesses: int


class LetrosoResponse(BaseModel):
    patterns: list[str]

    def __str__(self) -> str:
        return f"Accept | {'/'.join(self.patterns)}"


class LetrosoError(BaseModel):
    error: str

    def __str__(self) -> str:
        return f"Reject | {self.error}"


type LetrosoFeedback = LetrosoResponse | LetrosoError


class LetrosoFinalResult(BaseModel):
    num_found: int
    answers: list[str]

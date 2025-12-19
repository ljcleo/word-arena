from pydantic import BaseModel


class ConexoInfo(BaseModel):
    words: list[str]
    group_size: int
    max_guesses: int


class ConexoFeedback(BaseModel):
    accepted: bool
    message: str | None

    def __str__(self) -> str:
        if self.accepted:
            verdict: str = (
                "Wrong Guess" if self.message is None else f"Correct; Group Theme: {self.message}"
            )

            return f"Accept | {verdict}"
        else:
            return f"Reject | {self.message}"


class ConexoWordGroup(BaseModel):
    theme: str
    words: list[str]


class ConexoFinalResult(BaseModel):
    num_found: int
    groups: list[ConexoWordGroup]

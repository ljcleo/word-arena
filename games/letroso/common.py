from pydantic import BaseModel


class LetrosoInfo(BaseModel):
    num_targets: int
    max_letters: int
    max_guesses: int


class LetrosoResponse(BaseModel):
    results: list[str]

    def __str__(self) -> str:
        return f"Accept | {'/'.join(self.results)}"


class LetrosoError(BaseModel):
    error: str

    def __str__(self) -> str:
        return f"Reject | {self.error}"


type LetrosoResult = LetrosoResponse | LetrosoError

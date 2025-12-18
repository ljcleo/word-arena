from pydantic import BaseModel


class WordleInfo(BaseModel):
    num_targets: int
    max_guesses: int


class WordleResponse(BaseModel):
    patterns: list[str]

    def __str__(self) -> str:
        return f"Accept | {'/'.join(self.patterns)}"


class WordleError(BaseModel):
    error: str

    def __str__(self) -> str:
        return f"Reject | {self.error}"


type WordleFeedback = WordleResponse | WordleError

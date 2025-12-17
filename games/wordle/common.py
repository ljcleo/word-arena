from pydantic import BaseModel


class WordleInfo(BaseModel):
    num_targets: int
    max_accept_guesses: int


class WordleResponse(BaseModel):
    results: list[str]


class WordleError(BaseModel):
    error: str


type WordleResult = WordleResponse | WordleError


def format_wordle_result(result: WordleResult, /) -> str:
    return (
        f"Reject | {result.error}"
        if isinstance(result, WordleError)
        else f"Accept | {'/'.join(result.results)}"
    )

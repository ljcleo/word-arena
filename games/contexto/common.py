from pydantic import BaseModel


class ContextoResponse(BaseModel):
    word: str
    lemma: str
    distance: int


class ContextoError(BaseModel):
    error: str


type ContextoResult = ContextoResponse | ContextoError


def format_contexto_result(result: ContextoResult, /) -> str:
    return (
        f"Reject | {result.error}"
        if isinstance(result, ContextoError)
        else f"Accept | Lemmatized as {result.lemma}; Position {result.distance + 1}"
    )

from pydantic import BaseModel


class ContextoResponse(BaseModel):
    word: str
    lemma: str
    distance: int

    def __str__(self) -> str:
        return f"Accept | Lemmatized as {self.lemma}; Position {self.distance + 1}"


class ContextoError(BaseModel):
    error: str

    def __str__(self) -> str:
        return f"Reject | {self.error}"


type ContextoResult = ContextoResponse | ContextoError

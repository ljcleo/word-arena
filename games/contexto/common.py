from pydantic import BaseModel


class ContextoResponse(BaseModel):
    word: str
    lemma: str
    distance: int


class ContextoError(BaseModel):
    error: str

from pydantic import BaseModel


class TuringInfo(BaseModel):
    verifiers: list[list[str]]
    max_turns: int


class TuringGuess(BaseModel):
    code: int
    verifiers: list[int]


type TuringFeedback = list[bool] | bool | str


class TuringFinalResult(BaseModel):
    verdict: bool | None
    num_questions: int
    answer: int

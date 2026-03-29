from pydantic import BaseModel


class Note(BaseModel):
    law: str
    strategy: str


class Analysis(BaseModel):
    analysis: str
    plan: str


class Reflection(BaseModel):
    summary: str
    reflection: str

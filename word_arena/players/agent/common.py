from pydantic import BaseModel, Field


class Analysis(BaseModel):
    analysis: str = Field(title="Analysis")
    plan: str = Field(title="Plan")


class Reflection(BaseModel):
    summary: str = Field(title="Game Summary")
    reflection: str = Field(title="Reflection")

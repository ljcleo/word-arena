from pydantic import BaseModel


class ContextoHintExperience(BaseModel):
    law: str
    strategy: str

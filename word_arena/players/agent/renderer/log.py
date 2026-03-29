from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from ....common.player.renderer.log import BaseLogPlayerRenderer
from ..common import Analysis, Note, Reflection


class NoteLogPromptConfig(BaseModel):
    law: str
    strategy: str


class AnalysisLogPromptConfig(BaseModel):
    analysis: str
    plan: str


class ReflectionLogPromptConfig(BaseModel):
    summary: str
    reflection: str


class AgentLogPromptConfig(BaseModel):
    note: NoteLogPromptConfig
    analysis: AnalysisLogPromptConfig
    reflection: ReflectionLogPromptConfig


class AgentLogPlayerRenderer[IT, GT, FT, RT](
    BaseLogPlayerRenderer[AgentLogPromptConfig, Note, IT, Analysis, GT, FT, RT, Reflection]
):
    @override
    def format_note(self, *, note: Note) -> Iterator[tuple[str, str]]:
        prompt: NoteLogPromptConfig = self.prompt_config.note
        yield prompt.law, note.law
        yield prompt.strategy, note.strategy

    @override
    def format_analysis(self, *, analysis: Analysis) -> Iterator[tuple[str, str]]:
        prompt: AnalysisLogPromptConfig = self.prompt_config.analysis
        yield prompt.analysis, analysis.analysis
        yield prompt.plan, analysis.plan

    @override
    def format_reflection(self, *, reflection: Reflection) -> Iterator[tuple[str, str]]:
        prompt: ReflectionLogPromptConfig = self.prompt_config.reflection
        yield prompt.summary, reflection.summary
        yield prompt.reflection, reflection.reflection

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from typing import override

from pydantic import BaseModel

from ...formatter.agent import BaseAgentMemoryFormatter
from ...game.common import GameRecord
from ...llm.base import BaseLLM
from ...llm.common import Message
from ...memory.base import BaseMemory
from ...memory.common import Analysis, GameSummary, Reflection
from .utils import make_json_prompt, maybe_iter_with_title


class BaseAgentMemory[IT, HT, GT, FT, RT, NT: BaseModel](
    BaseMemory[IT, HT, GT, FT, RT, NT], BaseAgentMemoryFormatter[IT, HT, GT, FT, RT, NT], ABC
):
    def __init__(
        self, model: BaseLLM, note_cls: type[NT], log_func: Callable[[str, str], None], **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._model: BaseLLM = model
        self._note_cls: type[NT] = note_cls
        self._log_func: Callable[[str, str], None] = log_func

    @override
    def create_note(self) -> NT:
        note: NT = self._model.parse(
            Message.system(*self._make_system_prompt(status="You have not played the game yet.")),
            Message.human(
                "# Instruction",
                "Initialize some notes that help you make a good guess in a turn.",
                *self._make_note_prompt(),
            ),
            format=self._note_cls,
        )

        for key, value in self.format_note(note=note):
            self._log_func(key, value)

        return note

    @override
    def create_reflection(
        self, *, game_record: GameRecord[IT, HT, GT, FT, RT], latest_analysis: Analysis | None
    ) -> Reflection:
        reflection: Reflection = self._model.parse(
            Message.system(*self._make_system_prompt(status="You have played the game once.")),
            Message.human(
                *maybe_iter_with_title(
                    title="# Game Record",
                    sections=self.format_record(
                        game_record=game_record, latest_analysis=latest_analysis
                    ),
                ),
                "# Instruction",
                "Make a summary of the game process, then reflect on your performance.",
                *self._make_reflection_prompt(),
            ),
            format=Reflection,
        )

        for key, value in self.format_reflection(reflection=reflection):
            self._log_func(key, value)

        return reflection

    @override
    def update_note(self, *, history: Iterable[GameSummary[IT, HT, GT, FT, RT]], note: NT) -> NT:
        note = self._model.parse(
            Message.system(
                *self._make_system_prompt(status="You have played the game a few times.")
            ),
            Message.human(
                *maybe_iter_with_title(
                    title="# Current Notes", sections=self.format_note_xml(note=note)
                ),
                *maybe_iter_with_title(
                    title="# Trials", sections=self.format_history(history=history)
                ),
                "# Instruction",
                "Create some improved notes based on what you have learned from your trials.",
                *self._make_note_prompt(),
            ),
            format=self._note_cls,
        )

        for key, value in self.format_note(note=note):
            self._log_func(key, value)

        return note

    @abstractmethod
    def make_role_def_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_game_rule_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_note_detail_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def get_note_example(self) -> NT:
        raise NotImplementedError()

    def _make_system_prompt(self, *, status: str) -> Iterator[str]:
        yield from maybe_iter_with_title(title="# Identity", sections=self.make_role_def_prompt())
        yield from maybe_iter_with_title(title="# Game Rule", sections=self.make_game_rule_prompt())
        yield "# Current Status"
        yield status

    def _make_note_prompt(self) -> Iterator[str]:
        yield from self.make_note_detail_prompt()
        yield "Make your response clear and concise."
        yield make_json_prompt(example=self.get_note_example())

    def _make_reflection_prompt(self) -> Iterator[str]:
        yield from self.make_reflect_detail_prompt()
        yield "Make your response clear and concise."
        yield make_json_prompt(example=Reflection(summary="...", reflection="..."))

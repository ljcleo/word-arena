from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel

from ...formatter.agent import BaseAgentMemoryFormatter
from ...game.common import GameRecord
from ...llm.base import BaseLLM
from ...llm.common import Message
from ...memory.base import BaseMemory
from ...memory.common import Analysis, GameSummary, Reflection
from .common import TrialMode


class BaseAgentMemory[IT, HT, GT, FT, RT, ET: BaseModel](
    BaseMemory[IT, HT, GT, FT, RT, ET], BaseAgentMemoryFormatter[IT, HT, GT, FT, RT, ET], ABC
):
    def __init__(
        self,
        model: BaseLLM,
        experience_cls: type[ET],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._model: BaseLLM = model
        self._experience_cls: type[ET] = experience_cls

    @override
    def create_experience(self) -> ET:
        experience: ET = self._model.parse(
            Message.system(*self._make_system_prompt(trial_mode=TrialMode.NONE)),
            Message.human(
                *self.make_create_experience_prompt(),
                *self._make_experience_prompt(),
            ),
            format=self._experience_cls,
        )

        for section in self.format_experience(experience=experience):
            print(section)

        return experience

    @override
    def create_reflection(
        self, *, game_record: GameRecord[IT, HT, GT, FT, RT], latest_analysis: Analysis | None
    ) -> Reflection:
        reflection: Reflection = self._model.parse(
            Message.system(*self._make_system_prompt(trial_mode=TrialMode.SINGLE)),
            Message.human(
                *self.format_record(game_record=game_record, latest_analysis=latest_analysis)
            ),
            Message.human(
                "Now, reflect on your performance in the game.",
                "Make a summary of your guesses and summarize the lessons you have learned.",
                *self.make_reflect_detail_prompt(),
                "Make your response clear and simple in JSON format like "
                f"`{Reflection(summary='In this trial, ...', lessons='...').model_dump_json()}`.",
            ),
            format=Reflection,
        )

        for section in self.format_reflection(reflection=reflection):
            print(section)

        return reflection

    @override
    def update_experience(
        self, *, history: Iterable[GameSummary[IT, HT, GT, FT, RT]], old_experience: ET
    ) -> ET:
        new_experience: ET = self._model.parse(
            Message.system(*self._make_system_prompt(trial_mode=TrialMode.MULTIPLE)),
            Message.human(*self.format_history(history=history)),
            Message.human(*self.format_experience(experience=old_experience)),
            Message.human(
                *self.make_update_experience_prompt(),
                *self._make_experience_prompt(),
            ),
            format=self._experience_cls,
        )

        for section in self.format_experience(experience=new_experience):
            print(section)

        return new_experience

    @abstractmethod
    def make_role_def_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_game_rule_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_create_experience_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_update_experience_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def get_experience_example(self) -> ET:
        raise NotImplementedError()

    def _make_system_prompt(self, *, trial_mode: TrialMode) -> Iterator[str]:
        yield from self.make_role_def_prompt()
        yield "The following section describes an interactive guessing game:"

        for section in self.make_game_rule_prompt():
            yield "\n".join(f"> {line}" for line in section.split("\n"))

        yield (
            "Now, you are new to the game and have no trials yet."
            if trial_mode == TrialMode.NONE
            else "Now, you have played this game once."
            if trial_mode == TrialMode.SINGLE
            else "Now, you have played this game multiple times."
        )

    def _make_experience_prompt(self) -> Iterator[str]:
        yield "The notes should help you make a good guess in a turn."

        yield (
            "Make your response clear and simple in JSON format like "
            f"`{self.get_experience_example().model_dump_json()}`."
        )

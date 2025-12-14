import enum
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel

from agent.memory import BaseMemory
from common.player import BasePlayer
from llm.common import BaseLLM, Message


@enum.unique
class PromptMode(enum.Enum):
    SIMPLE = enum.auto()
    DIRECT = enum.auto()
    MULTI_TURN = enum.auto()


class SimpleGuess(BaseModel):
    guess: str


class FullGuess(BaseModel):
    analysis: str
    plan: str
    guess: str


class BaseAgentPlayer[GT, PT, AT, RT, FT, TT: BaseModel, ET: BaseModel](
    BasePlayer[GT, PT, AT, RT], ABC
):
    def __init__(
        self,
        *,
        model: BaseLLM,
        memory: BaseMemory[GT, PT, AT, RT, FT, TT, ET],
        prompt_mode: PromptMode,
    ):
        self._model: BaseLLM = model
        self._prompt_mode: PromptMode = prompt_mode
        self._memory: BaseMemory[GT, PT, AT, RT, FT, TT, ET] = memory

    @property
    def memory(self) -> BaseMemory[GT, PT, AT, RT, FT, TT, ET]:
        return self._memory

    @override
    def prepare(self, *, game_info: GT) -> None:
        self._memory.prepare(game_info=game_info)

    @override
    def guess(self, *, hint: PT) -> AT:
        messages: list[Message] = list(
            self.make_guess_info_messages(
                experience=self._memory.experience,
                current_trajectory=self._memory.current_trajectory,
                hint=hint,
            )
        )

        raw_guess: str

        if self._prompt_mode == PromptMode.DIRECT:
            full_guess: FullGuess = self._model.parse(
                *messages,
                Message.human(*self.make_full_guess_prompt(hint=hint)),
                format=FullGuess,
            )

            print("AI Analysis:", full_guess.analysis)
            print("AI Plan:", full_guess.plan)
            raw_guess = full_guess.guess
        else:
            if self._prompt_mode == PromptMode.MULTI_TURN:
                messages.append(Message.human(*self.make_analyze_prompt()))
                analysis: str = self._model.query(*messages)
                print("AI Analysis:", analysis)
                messages.append(Message.ai(analysis))

                messages.append(Message.human(*self.make_plan_prompt()))
                plan: str = self._model.query(*messages)
                print("AI Plan:", plan)
                messages.append(Message.ai(plan))

            raw_guess = self._model.parse(
                *messages,
                Message.human(*self.make_simple_guess_prompt(hint=hint)),
                format=SimpleGuess,
            ).guess

        guess: AT = self.process_guess(hint=hint, raw_guess=raw_guess)
        print("AI Guess:", raw_guess, guess)
        return guess

    @override
    def digest(self, *, hint: PT, guess: AT, result: RT) -> None:
        print("Result:", result)
        self._memory.digest(hint=hint, guess=guess, result=result)

    @abstractmethod
    def make_guess_info_messages(
        self, *, experience: ET | None, current_trajectory: Iterable[tuple[PT, AT, RT]], hint: PT
    ) -> Iterator[Message]:
        raise NotImplementedError()

    @abstractmethod
    def make_full_guess_prompt(self, *, hint: PT) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_analyze_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_plan_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_simple_guess_prompt(self, *, hint: PT) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def process_guess(self, *, hint: PT, raw_guess: str) -> AT:
        raise NotImplementedError()

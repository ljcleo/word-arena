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


class Analysis(BaseModel):
    analysis: str | None
    plan: str | None


class FullGuess(BaseModel):
    analysis: Analysis
    guess: str


class AgentMemory[GT, PT, AT, RT, FT, TT: BaseModel, ET: BaseModel](
    BaseMemory[GT, PT, AT, RT, FT, Analysis, TT, ET], ABC
):
    pass


class BaseAgentPlayer[GT, PT, AT, RT, FT, TT: BaseModel, ET: BaseModel](
    BasePlayer[GT, PT, AT, RT], ABC
):
    def __init__(
        self,
        *,
        model: BaseLLM,
        memory: BaseMemory[GT, PT, AT, RT, FT, Analysis, TT, ET],
        prompt_mode: PromptMode,
    ):
        self._model: BaseLLM = model
        self._prompt_mode: PromptMode = prompt_mode
        self._memory: BaseMemory[GT, PT, AT, RT, FT, Analysis, TT, ET] = memory

    @property
    def memory(self) -> BaseMemory[GT, PT, AT, RT, FT, Analysis, TT, ET]:
        return self._memory

    @override
    def prepare(self, *, game_info: GT) -> None:
        self._memory.prepare(game_info=game_info)

    @override
    def guess(self, *, hint: PT) -> AT:
        messages: list[Message] = list(
            self.make_guess_info_messages(
                game_info=self._memory.game_info,
                experience=self._memory.experience,
                current_trajectory=self._memory.current_trajectory,
                hint=hint,
            )
        )

        full_analysis: Analysis
        raw_guess: str

        if self._prompt_mode == PromptMode.DIRECT:
            full_guess: FullGuess = self._model.parse(
                *messages,
                Message.human(*self.make_full_guess_prompt(hint=hint)),
                format=FullGuess,
            )

            print("AI Analysis:", full_guess.analysis.analysis)
            print("AI Plan:", full_guess.analysis.plan)
            raw_guess = full_guess.guess
            full_analysis = full_guess.analysis
        else:
            analysis: str | None = None
            plan: str | None = None

            if self._prompt_mode == PromptMode.MULTI_TURN:
                messages.append(Message.human(*self.make_analyze_prompt()))
                analysis = self._model.query(*messages)
                print("AI Analysis:", analysis)
                messages.append(Message.ai(analysis))

                messages.append(Message.human(*self.make_plan_prompt()))
                plan = self._model.query(*messages)
                print("AI Plan:", plan)
                messages.append(Message.ai(plan))

            raw_guess = self._model.parse(
                *messages,
                Message.human(*self.make_simple_guess_prompt(hint=hint)),
                format=SimpleGuess,
            ).guess

            full_analysis = Analysis(analysis=analysis, plan=plan)

        self._memory.update_analysis(analysis=full_analysis)
        guess: AT = self.process_guess(hint=hint, raw_guess=raw_guess)
        print("AI Guess:", raw_guess, guess)
        return guess

    @override
    def digest(self, *, hint: PT, guess: AT, result: RT) -> None:
        print("Result:", result)
        self._memory.digest(hint=hint, guess=guess, result=result)

    @abstractmethod
    def make_guess_info_messages(
        self,
        *,
        game_info: GT,
        experience: ET,
        current_trajectory: Iterable[tuple[PT, tuple[Analysis, AT], RT]],
        hint: PT,
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

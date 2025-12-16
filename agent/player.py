import enum
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import Any, override

from pydantic import BaseModel, Field, create_model

from agent.memory import BaseMemory, Turn
from common.player import BasePlayer
from llm.common import BaseLLM, Message


@enum.unique
class PromptMode(enum.Enum):
    SIMPLE = enum.auto()
    DIRECT = enum.auto()
    MULTI_TURN = enum.auto()


class Analysis(BaseModel):
    analysis: str
    plan: str


class AgentMemory[GT, PT, AT, RT, FT, TT: BaseModel, ET: BaseModel](
    BaseMemory[GT, PT, Analysis, AT, RT, FT, TT, ET], ABC
):
    pass


class BaseAgentPlayer[GT, PT, AT, RT, FT, TT: BaseModel, ET: BaseModel](
    BasePlayer[GT, PT, AT, RT], ABC
):
    def __init__(
        self,
        *,
        model: BaseLLM,
        memory: BaseMemory[GT, PT, Analysis, AT, RT, FT, TT, ET],
        prompt_mode: PromptMode,
    ):
        self._model: BaseLLM = model
        self._prompt_mode: PromptMode = prompt_mode
        self._memory: BaseMemory[GT, PT, Analysis, AT, RT, FT, TT, ET] = memory
        self._guess_model: type[BaseModel]

        if prompt_mode == PromptMode.DIRECT:
            self._guess_model = create_model("Guess", analysis=Analysis, guess=str)
        else:
            self._guess_model = create_model("Guess", guess=str)

    @property
    def memory(self) -> BaseMemory[GT, PT, Analysis, AT, RT, FT, TT, ET]:
        return self._memory

    @override
    def prepare(self, *, game_info: GT) -> None:
        self._memory.prepare(game_info=game_info)
        self._current_analysis: Analysis | None = None

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

        raw_guess: str

        if self._prompt_mode == PromptMode.DIRECT:
            full_guess: BaseModel = self._model.parse(
                *messages,
                Message.human(*self.make_full_guess_prompt(hint=hint)),
                format=self._guess_model,
            )

            self._current_analysis = getattr(full_guess, "analysis")
            raw_guess = getattr(full_guess, "guess")
            assert self._current_analysis is not None
            print("AI Analysis:", self._current_analysis.analysis)
            print("AI Plan:", self._current_analysis.plan)
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

                self._current_analysis = Analysis(analysis=analysis, plan=plan)

            raw_guess = getattr(
                self._model.parse(
                    *messages,
                    Message.human(*self.make_simple_guess_prompt(hint=hint)),
                    format=self._guess_model,
                ),
                "guess",
            )

        guess: AT = self.process_guess(hint=hint, raw_guess=raw_guess)
        print("AI Guess:", raw_guess, guess)
        return guess

    @override
    def digest(self, *, hint: PT, guess: AT, result: RT) -> None:
        print("Result:", result)
        self._memory.digest(hint=hint, analysis=self._current_analysis, guess=guess, result=result)

    @abstractmethod
    def make_guess_info_messages(
        self,
        *,
        game_info: GT,
        experience: ET,
        current_trajectory: Iterable[Turn[PT, Analysis, AT, RT]],
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


class BaseParallelAgentPlayer[GT, AT, RT, FT, TT: BaseModel, ET: BaseModel](
    BasePlayer[GT, None, AT, RT], ABC
):
    def __init__(
        self,
        *,
        model: BaseLLM,
        memory: BaseMemory[GT, None, Analysis, AT, RT, FT, TT, ET],
        prompt_mode: PromptMode,
        max_parallel_guesses: int | None,
    ):
        self._model: BaseLLM = model
        self._prompt_mode: PromptMode = prompt_mode
        self._max_parallel_guesses: int | None = max_parallel_guesses
        self._memory: BaseMemory[GT, None, Analysis, AT, RT, FT, TT, ET] = memory
        self._guess_model: type[BaseModel]

        guesses_def: tuple[type[list[str]], Any] = (
            list[str],
            Field(min_length=1, max_length=max_parallel_guesses),
        )

        if prompt_mode == PromptMode.DIRECT:
            self._guess_model = create_model("Guess", analysis=Analysis, guesses=guesses_def)
        else:
            self._guess_model = create_model("Guess", guesses=guesses_def)

    @property
    def max_parallel_guesses(self) -> int | None:
        return self._max_parallel_guesses

    @property
    def memory(self) -> BaseMemory[GT, None, Analysis, AT, RT, FT, TT, ET]:
        return self._memory

    @override
    def prepare(self, *, game_info: GT) -> None:
        self._memory.prepare(game_info=game_info)
        self._current_analysis: Analysis | None = None
        self._guess_buffer: list[str] = []

    @override
    def guess(self, *, hint: None) -> AT:
        if len(self._guess_buffer) == 0:
            messages: list[Message] = list(
                self.make_guess_info_messages(
                    game_info=self._memory.game_info,
                    experience=self._memory.experience,
                    current_trajectory=self._memory.current_trajectory,
                )
            )

            raw_guesses: list[str]

            if self._prompt_mode == PromptMode.DIRECT:
                full_guess: BaseModel = self._model.parse(
                    *messages,
                    Message.human(*self.make_full_guess_prompt()),
                    format=self._guess_model,
                )

                self._current_analysis = getattr(full_guess, "analysis")
                raw_guesses = getattr(full_guess, "guesses")
                assert self._current_analysis is not None
                print("AI Analysis:", self._current_analysis.analysis)
                print("AI Plan:", self._current_analysis.plan)
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

                    self._current_analysis = Analysis(analysis=analysis, plan=plan)

                raw_guesses = getattr(
                    self._model.parse(
                        *messages,
                        Message.human(*self.make_simple_guess_prompt()),
                        format=self._guess_model,
                    ),
                    "guesses",
                )

            self._guess_buffer.extend(reversed(raw_guesses))

        raw_guess: str = self._guess_buffer.pop()
        guess: AT = self.process_guess(raw_guess=raw_guess)
        print("AI Guess:", raw_guess, guess)
        return guess

    @override
    def digest(self, *, hint: None, guess: AT, result: RT) -> None:
        print("Result:", result)
        self._memory.digest(hint=hint, analysis=self._current_analysis, guess=guess, result=result)
        self._current_analysis = None

    @abstractmethod
    def make_guess_info_messages(
        self,
        *,
        game_info: GT,
        experience: ET,
        current_trajectory: Iterable[Turn[None, Analysis, AT, RT]],
    ) -> Iterator[Message]:
        raise NotImplementedError()

    @abstractmethod
    def make_full_guess_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_analyze_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_plan_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_simple_guess_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def process_guess(self, *, raw_guess: str) -> AT:
        raise NotImplementedError()

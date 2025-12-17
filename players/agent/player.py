import enum
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from typing import override

from pydantic import BaseModel, create_model

from common.player import BasePlayer
from llm.common import BaseLLM, Message
from players.agent.memory import Analysis, BaseMemory, Turn


@enum.unique
class PromptMode(enum.Enum):
    SIMPLE = enum.auto()
    DIRECT = enum.auto()
    MULTI_TURN = enum.auto()


class BaseAgentPlayer[GT, PT, AT, RT, FT, ET: BaseModel](BasePlayer[GT, PT, AT, RT], ABC):
    def __init__(
        self, *, model: BaseLLM, memory: BaseMemory[GT, PT, AT, RT, FT, ET], prompt_mode: PromptMode
    ):
        self._model: BaseLLM = model
        self._prompt_mode: PromptMode = prompt_mode
        self._memory: BaseMemory[GT, PT, AT, RT, FT, ET] = memory
        self._guess_model: type[BaseModel]

        if prompt_mode == PromptMode.DIRECT:
            self._guess_model = create_model("Guess", analysis=Analysis, guess=str)
        else:
            self._guess_model = create_model("Guess", guess=str)

    @property
    def memory(self) -> BaseMemory[GT, PT, AT, RT, FT, ET]:
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
                Message.human(
                    *self.make_full_guess_prompt(
                        hint=hint,
                        make_example=lambda e: self._guess_model(
                            analysis=Analysis.example(), guess=e
                        ).model_dump_json(),
                    )
                ),
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
                    Message.human(
                        *self.make_simple_guess_prompt(
                            hint=hint,
                            make_example=lambda e: self._guess_model(guess=e).model_dump_json(),
                        )
                    ),
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
        current_trajectory: Iterable[Turn[PT, AT, RT]],
        hint: PT,
    ) -> Iterator[Message]:
        raise NotImplementedError()

    @abstractmethod
    def make_full_guess_prompt(
        self, *, hint: PT, make_example: Callable[[str], str]
    ) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_analyze_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_plan_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_simple_guess_prompt(
        self, *, hint: PT, make_example: Callable[[str], str]
    ) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def process_guess(self, *, hint: PT, raw_guess: str) -> AT:
        raise NotImplementedError()

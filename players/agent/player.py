import enum
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from typing import override

from pydantic import BaseModel, create_model

from llm.common import BaseLLM, Message
from players.agent.memory import Analysis, BaseMemory, Turn
from players.common import BaseIOPlayer


@enum.unique
class PromptMode(enum.Enum):
    SIMPLE = enum.auto()
    DIRECT = enum.auto()
    MULTI_TURN = enum.auto()


class BaseAgentPlayer[GT, PT, AT, RT, FT, ET: BaseModel](BaseIOPlayer[GT, PT, AT, RT], ABC):
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
        self._latest_analysis: Analysis | None = None

    @override
    def make_raw_guess(self, *, hint: PT) -> str:
        messages: list[Message] = list(
            self.make_guess_info_messages(
                game_info=self._memory.game_info,
                experience=self._memory.experience,
                current_trajectory=self._memory.current_trajectory,
                latest_analysis=self._latest_analysis,
                hint=hint,
            )
        )

        self._latest_analysis = None
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

            self._latest_analysis = getattr(full_guess, "analysis")
            raw_guess = getattr(full_guess, "guess")
            assert self._latest_analysis is not None
            print("AI Past Analysis Summary:", self._latest_analysis.past_analysis_summary)
            print("AI Current Analysis:", self._latest_analysis.current_analysis)
            print("AI Plan:", self._latest_analysis.plan)
        else:
            if self._prompt_mode == PromptMode.MULTI_TURN:
                past_analysis_summary: str = ""

                if self.memory.num_guesses > 0:
                    messages.append(Message.human(*self.make_summarize_analysis_prompt()))
                    past_analysis_summary = self._model.query(*messages)
                    print("AI Past Analysis Summary:", past_analysis_summary)
                    messages.append(Message.ai(past_analysis_summary))

                messages.append(Message.human(*self.make_analyze_prompt()))
                current_analysis: str = self._model.query(*messages)
                print("AI Current Analysis:", current_analysis)
                messages.append(Message.ai(current_analysis))

                messages.append(Message.human(*self.make_plan_prompt()))
                plan: str = self._model.query(*messages)
                print("AI Plan:", plan)
                messages.append(Message.ai(plan))

                self._latest_analysis = Analysis(
                    past_analysis_summary=past_analysis_summary,
                    current_analysis=current_analysis,
                    plan=plan,
                )

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

        print("AI Guess:", raw_guess)
        return raw_guess

    @override
    def digest(self, *, hint: PT, guess: AT, result: RT) -> None:
        super().digest(hint=hint, guess=guess, result=result)
        self._memory.digest(hint=hint, analysis=self._latest_analysis, guess=guess, result=result)

    @abstractmethod
    def make_guess_info_messages(
        self,
        *,
        game_info: GT,
        experience: ET,
        current_trajectory: Iterable[Turn[PT, AT, RT]],
        latest_analysis: Analysis | None,
        hint: PT,
    ) -> Iterator[Message]:
        raise NotImplementedError()

    @abstractmethod
    def make_full_guess_prompt(
        self, *, hint: PT, make_example: Callable[[str], str]
    ) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_summarize_analysis_prompt(self) -> Iterator[str]:
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

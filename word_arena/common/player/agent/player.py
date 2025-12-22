from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any, override

from pydantic import BaseModel, create_model

from ...formatter.agent import BaseAgentPlayerFormatter
from ...llm.base import BaseLLM, Message
from ...memory.common import Analysis
from ..log import BaseLogPlayer
from .common import PromptMode
from .memory import BaseAgentMemory


class BaseAgentPlayer[IT, HT, GT: BaseModel, FT, ET: BaseModel](
    BaseLogPlayer[IT, HT, GT, FT], BaseAgentPlayerFormatter[IT, HT, GT, FT, ET], ABC
):
    def __init__(
        self,
        *,
        memory: BaseAgentMemory[IT, HT, GT, FT, Any, ET],
        model: BaseLLM,
        prompt_mode: PromptMode,
        guess_cls: type[GT],
    ):
        self._memory: BaseAgentMemory[IT, HT, GT, FT, Any, ET] = memory
        self._model: BaseLLM = model
        self._prompt_mode: PromptMode = prompt_mode
        self._guess_cls: type[GT] = guess_cls

        if prompt_mode == PromptMode.DIRECT:
            self._guess_model: type[BaseModel] = create_model(
                "Guess", analysis=Analysis, guess=guess_cls
            )

        self.memory.init_experience()

    @property
    def memory(self) -> BaseAgentMemory[IT, HT, GT, FT, Any, ET]:
        return self._memory

    @override
    def prepare(self, *, game_info: IT) -> None:
        super().prepare(game_info=game_info)
        self.memory.prepare(game_info=game_info)
        self._latest_analysis: Analysis | None = None

    @override
    def digest(self, *, hint: HT, guess: GT, feedback: FT) -> None:
        super().digest(hint=hint, guess=guess, feedback=feedback)

        self.memory.digest(
            hint=hint, analysis=self._latest_analysis, guess=guess, feedback=feedback
        )

    @override
    def make_guess(self, *, hint: HT) -> GT:
        messages: list[Message] = [
            Message.system(*self._make_system_prompt()),
            Message.human(
                *self.format_in_game_record(
                    game_info=self.memory.game_info,
                    trajectory=self.memory.current_trajectory,
                    latest_analysis=self._latest_analysis,
                ),
                *self.format_hint(game_info=self.memory.game_info, hint=hint),
            ),
        ]

        self._latest_analysis = None
        guess: GT

        if self._prompt_mode == PromptMode.DIRECT:
            messages.append(
                Message.human(*self.make_full_guess_prompt(), *self._make_guess_prompt(hint=hint))
            )

            full_guess: BaseModel = self._model.parse(*messages, format=self._guess_model)
            self._latest_analysis = getattr(full_guess, "analysis")
            guess = getattr(full_guess, "guess")
            assert self._latest_analysis is not None
        else:
            if self._prompt_mode == PromptMode.MULTI_TURN:
                past_analysis_summary: str = ""

                if self.memory.num_guesses > 0:
                    messages.append(Message.human(*self.make_summarize_analysis_prompt()))
                    past_analysis_summary = self._model.query(*messages)
                    messages.append(Message.ai(past_analysis_summary))

                messages.append(Message.human(*self.make_analyze_prompt()))
                current_analysis: str = self._model.query(*messages)
                messages.append(Message.ai(current_analysis))

                messages.append(
                    Message.human(
                        *self.make_plan_prompt(), *self.make_guess_detail_prompt(hint=hint)
                    )
                )

                plan: str = self._model.query(*messages)
                messages.append(Message.ai(plan))

                self._latest_analysis = Analysis(
                    past_analysis_summary=past_analysis_summary,
                    current_analysis=current_analysis,
                    plan=plan,
                )

            messages.append(
                Message.human(*self.make_simple_guess_prompt(), *self._make_guess_prompt(hint=hint))
            )

            guess = self._model.parse(*messages, format=self._guess_cls)

        if self._latest_analysis is not None:
            for section in self.format_analysis(analysis=self._latest_analysis):
                print(section)

        return guess

    @abstractmethod
    def make_role_def_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_game_rule_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_full_guess_prompt(self) -> Iterator[str]:
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
    def make_simple_guess_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_guess_detail_prompt(self, *, hint: HT) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def get_guess_example(self, *, hint: HT) -> GT:
        raise NotImplementedError()

    def _make_system_prompt(self) -> Iterator[str]:
        yield from self.make_role_def_prompt()
        yield from self.make_game_rule_prompt()
        yield "Current Experience:"
        yield from self.format_experience(experience=self.memory.experience)

    def _make_guess_prompt(self, *, hint: HT) -> Iterator[str]:
        yield from self.make_guess_detail_prompt(hint=hint)
        guess_example: BaseModel = self.get_guess_example(hint=hint)

        if self._prompt_mode == PromptMode.DIRECT:
            guess_example = self._guess_model(
                analysis=Analysis(past_analysis_summary="...", current_analysis="...", plan="..."),
                guess=guess_example,
            )

        yield (f"Respond in JSON format like `{guess_example.model_dump_json()}`.")

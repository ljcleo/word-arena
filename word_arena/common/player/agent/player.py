from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import override

from pydantic import BaseModel, create_model

from ...formatter.agent import BaseAgentFormatter
from ...llm.base import BaseLLM, Message
from ...memory.common import Analysis
from ..log import BaseLogPlayer
from .common import PromptMode
from .memory import BaseAgentMemory


class BaseAgentPlayer[IT, HT, GT, FT, RT, ET: BaseModel](BaseLogPlayer[IT, HT, GT, FT], ABC):
    def __init__(
        self,
        *,
        memory: BaseAgentMemory[IT, HT, GT, FT, RT, ET],
        model: BaseLLM,
        prompt_mode: PromptMode,
        agent_formatter_cls: type[BaseAgentFormatter[IT, HT, GT, FT, RT, ET]],
    ):
        super().__init__(in_game_formatter_cls=agent_formatter_cls.get_in_game_formatter_cls())
        self._memory: BaseAgentMemory[IT, HT, GT, FT, RT, ET] = memory
        self._model: BaseLLM = model
        self._prompt_mode: PromptMode = prompt_mode
        self._guess_model: type[BaseModel]

        self._agent_formatter_cls: type[BaseAgentFormatter[IT, HT, GT, FT, RT, ET]] = (
            agent_formatter_cls
        )

        if prompt_mode == PromptMode.DIRECT:
            self._guess_model = create_model("Guess", analysis=Analysis, guess=str)
        else:
            self._guess_model = create_model("Guess", guess=str)

        self.memory.init_experience()

    @property
    def memory(self) -> BaseAgentMemory[IT, HT, GT, FT, RT, ET]:
        return self._memory

    @property
    def agent_formatter_cls(self) -> type[BaseAgentFormatter[IT, HT, GT, FT, RT, ET]]:
        return self._agent_formatter_cls

    @override
    def prepare(self, *, game_info: IT) -> None:
        super().prepare(game_info=game_info)
        self.memory.prepare(game_info=game_info)
        self._latest_analysis: Analysis | None = None

    @override
    def make_raw_guess(self, *, hint: HT) -> str:
        messages: list[Message] = [
            Message.system(*self._make_system_prompt()),
            Message.human(
                *self.agent_formatter_cls.format_in_game_record(
                    game_info=self.memory.game_info,
                    trajectory=self.memory.current_trajectory,
                    latest_analysis=self._latest_analysis,
                ),
                *self.in_game_formatter_cls.format_hint(game_info=self.memory.game_info, hint=hint),
            ),
        ]

        self._latest_analysis = None
        raw_guess: str

        if self._prompt_mode == PromptMode.DIRECT:
            messages.append(
                Message.human(*self.make_full_guess_prompt(), *self._make_guess_prompt(hint=hint))
            )

            full_guess: BaseModel = self._model.parse(*messages, format=self._guess_model)
            self._latest_analysis = getattr(full_guess, "analysis")
            raw_guess = getattr(full_guess, "guess")
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

            raw_guess = getattr(self._model.parse(*messages, format=self._guess_model), "guess")

        if self._latest_analysis is not None:
            for section in self.agent_formatter_cls.format_analysis(analysis=self._latest_analysis):
                print(section)

        print("AI Guess:", raw_guess)
        return raw_guess

    @override
    def digest(self, *, hint: HT, guess: GT, feedback: FT) -> None:
        super().digest(hint=hint, guess=guess, feedback=feedback)

        self.memory.digest(
            hint=hint, analysis=self._latest_analysis, guess=guess, feedback=feedback
        )

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
    def get_raw_guess_example(self, *, hint: HT) -> str:
        raise NotImplementedError()

    def _make_system_prompt(self) -> Iterator[str]:
        yield from self.make_role_def_prompt()
        yield from self.make_game_rule_prompt()
        yield "Current Experience:"
        yield from self._agent_formatter_cls.format_experience(experience=self.memory.experience)

    def _make_guess_prompt(self, *, hint: HT) -> Iterator[str]:
        yield from self.make_guess_detail_prompt(hint=hint)
        raw_guess_example: str = self.get_raw_guess_example(hint=hint)

        guess_example: BaseModel = (
            self._guess_model(
                analysis=Analysis(past_analysis_summary="...", current_analysis="...", plan="..."),
                guess=raw_guess_example,
            )
            if self._prompt_mode == PromptMode.DIRECT
            else self._guess_model(guess=raw_guess_example)
        )

        yield (f"Respond in JSON format like `{guess_example.model_dump_json()}`.")

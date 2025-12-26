from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import Any, override

from pydantic import BaseModel, create_model

from ...formatter.agent import BaseAgentPlayerFormatter
from ...llm.base import BaseLLM, Message
from ...memory.common import Analysis
from ..log import BaseLogPlayer
from .memory import BaseAgentMemory
from .utils import make_json_prompt, maybe_iter_with_title


class BaseAgentPlayer[IT, HT, GT: BaseModel, FT, NT: BaseModel](
    BaseLogPlayer[IT, HT, GT, FT], BaseAgentPlayerFormatter[IT, HT, GT, FT, NT], ABC
):
    def __init__(
        self,
        *,
        memory: BaseAgentMemory[IT, HT, GT, FT, Any, NT],
        model: BaseLLM,
        do_analyze: bool,
        guess_cls: type[GT],
        player_log_func: Callable[[str], None],
        agent_log_func: Callable[[str], None],
        **kwargs,
    ):
        super().__init__(player_log_func=player_log_func, **kwargs)
        self._memory: BaseAgentMemory[IT, HT, GT, FT, Any, NT] = memory
        self._model: BaseLLM = model
        self._do_analyze: bool = do_analyze
        self._guess_cls: type[GT] = guess_cls
        self._agent_log_func: Callable[[str], None] = agent_log_func

        if do_analyze:
            self._guess_model: type[BaseModel] = create_model(
                "Guess", analysis=Analysis, guess=guess_cls
            )

        self.memory.init_note()

    @property
    def memory(self) -> BaseAgentMemory[IT, HT, GT, FT, Any, NT]:
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
            Message.human(*self._make_human_prompt(hint=hint)),
        ]

        self._latest_analysis = None
        guess: GT

        if self._do_analyze:
            full_guess: BaseModel = self._model.parse(*messages, format=self._guess_model)
            self._latest_analysis = getattr(full_guess, "analysis")
            guess = getattr(full_guess, "guess")
            assert self._latest_analysis is not None
        else:
            guess = self._model.parse(*messages, format=self._guess_cls)

        if self._latest_analysis is not None:
            for key, value in self.format_analysis(analysis=self._latest_analysis):
                self._agent_log_func(f"{key}: {value}")

        return guess

    @abstractmethod
    def make_role_def_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_game_rule_prompt(self) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_guess_detail_prompt(self, *, hint: HT) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def get_guess_example(self, *, hint: HT) -> GT:
        raise NotImplementedError()

    def _make_system_prompt(self) -> Iterator[str]:
        yield from maybe_iter_with_title(title="# Identity", sections=self.make_role_def_prompt())
        yield from maybe_iter_with_title(title="# Game Rule", sections=self.make_game_rule_prompt())

        yield from maybe_iter_with_title(
            title="# Current Notes", sections=self.format_note_xml(note=self.memory.note)
        )

    def _make_human_prompt(self, *, hint: HT) -> Iterator[str]:
        yield from maybe_iter_with_title(
            title="# Game Info", sections=self.format_game_info_xml(game_info=self.memory.game_info)
        )

        yield from maybe_iter_with_title(
            title="# Guess History",
            sections=self.format_trajectory(
                game_info=self.memory.game_info, trajectory=self.memory.current_trajectory
            ),
        )

        yield from maybe_iter_with_title(
            title="# Latest Analysis",
            sections=()
            if self._latest_analysis is None
            else self.format_analysis_xml(analysis=self._latest_analysis),
        )

        yield from maybe_iter_with_title(
            title="# New Turn Info",
            sections=self.format_hint_xml(game_info=self.memory.game_info, hint=hint),
        )

        yield "# Instruction"

        if self._do_analyze:
            if self.memory.num_guesses == 0:
                yield "Analyze the game carefully, then plan and make your new guess."
            else:
                yield (
                    "Analyze the game carefully with previous analysis and latest feedback, "
                    "then plan and make your new guess."
                )
        else:
            yield "Analyze the game carefully and make your new guess."

        yield from self.make_guess_detail_prompt(hint=hint)
        yield "Make your response clear and concise."
        guess_example: BaseModel = self.get_guess_example(hint=hint)

        yield make_json_prompt(
            example=self._guess_model(
                analysis=Analysis(analysis="...", plan="..."), guess=guess_example
            )
            if self._do_analyze
            else guess_example
        )

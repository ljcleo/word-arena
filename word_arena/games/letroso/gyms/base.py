from collections.abc import Callable
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo
from ..formatters.base import LetrosoFinalResultFormatter
from ..generators.common import LetrosoConfig


class LetrosoConfigGym[**P](
    BaseConfigGym[
        LetrosoConfig, LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult, P
    ],
    LetrosoFinalResultFormatter,
):
    pass


class LetrosoExampleConfigGym(LetrosoConfigGym):
    def __init__(
        self, *, log_func: Callable[[str], None], input_func: Callable[[str], str], **kwargs
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._input_func: Callable[[str], str] = input_func

    @override
    def create_config(self) -> LetrosoConfig:
        return LetrosoConfig(
            max_letters=int(self._input_func("Max Input Letters: ")),
            max_guesses=int(self._input_func("Max Guesses: ")),
            game_ids=[
                int(self._input_func(f"Word ID {i + 1}: "))
                for i in range(int(self._input_func("Num Targets: ")))
            ],
        )

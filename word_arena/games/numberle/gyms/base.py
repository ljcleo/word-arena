from collections.abc import Callable
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import NumberleFeedback, NumberleFinalResult, NumberleGuess, NumberleInfo
from ..formatters.base import NumberleFinalResultFormatter
from ..generators.common import NumberleConfig, NumberleMetaConfig


class NumberleConfigGym[**P](
    BaseConfigGym[
        NumberleMetaConfig,
        NumberleConfig,
        NumberleInfo,
        None,
        NumberleGuess,
        NumberleFeedback,
        NumberleFinalResult,
        P,
    ],
    NumberleFinalResultFormatter,
):
    pass


class NumberleExampleConfigGym(NumberleConfigGym):
    def __init__(
        self, *, log_func: Callable[[str], None], input_func: Callable[[str], str], **kwargs
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._input_func: Callable[[str], str] = input_func

    @override
    def create_config(self, *, meta_config: NumberleMetaConfig) -> NumberleConfig:
        eq_length: int = int(self._input_func("Equation Length: "))
        max_game_id: int = meta_config.get_game_count(eq_length=eq_length) - 1

        return NumberleConfig(
            eq_length=eq_length,
            max_guesses=int(self._input_func("Max Guesses: ")),
            game_ids=[
                int(self._input_func(f"Word ID {i + 1} (0--{max_game_id}): "))
                for i in range(int(self._input_func("Num Targets: ")))
            ],
        )

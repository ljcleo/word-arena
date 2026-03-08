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
        self, *, log_func: Callable[[str, str], None], input_func: Callable[[str], str], **kwargs
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._input_func: Callable[[str], str] = input_func

    @override
    def create_config(self, *, meta_config: NumberleMetaConfig) -> NumberleConfig:
        eq_length: int = int(
            self._input_func(
                f"Equation Length ({'/'.join(map(str, meta_config.eq_length_pool))}): "
            )
        )

        return NumberleConfig(
            eq_length=eq_length,
            max_guesses=int(self._input_func("Max Guesses: ")),
            game_ids=meta_config.select_game_ids(
                eq_length=eq_length,
                selector=lambda n: (
                    int(self._input_func(f"Equation ID {i + 1} (0--{n - 1}): "))
                    for i in range(int(self._input_func("Num Targets: ")))
                ),
            ),
        )

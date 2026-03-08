from collections.abc import Callable
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo
from ..formatters.base import ConexoFinalResultFormatter
from ..generators.common import ConexoConfig, ConexoMetaConfig


class ConexoConfigGym[**P](
    BaseConfigGym[
        ConexoMetaConfig,
        ConexoConfig,
        ConexoInfo,
        None,
        ConexoGuess,
        ConexoFeedback,
        ConexoFinalResult,
        P,
    ],
    ConexoFinalResultFormatter,
):
    pass


class ConexoExampleConfigGym(ConexoConfigGym):
    def __init__(
        self, *, log_func: Callable[[str, str], None], input_func: Callable[[str], str], **kwargs
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._input_func: Callable[[str], str] = input_func

    @override
    def create_config(self, *, meta_config: ConexoMetaConfig) -> ConexoConfig:
        return ConexoConfig(
            max_guesses=int(self._input_func("Max Guesses: ")),
            game_id=meta_config.select_game_id(
                selector=lambda n: int(self._input_func(f"Game ID (0--{n - 1}): "))
            ),
        )

from collections.abc import Callable
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo
from ..formatters.base import ConexoFinalResultFormatter
from ..generators.common import ConexoConfig


class ConexoConfigGym[**P](
    BaseConfigGym[
        ConexoConfig, ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoFinalResult, P
    ],
    ConexoFinalResultFormatter,
):
    pass


class ConexoExampleConfigGym(ConexoConfigGym):
    def __init__(
        self, *, log_func: Callable[[str], None], input_func: Callable[[str], str], **kwargs
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._input_func: Callable[[str], str] = input_func

    @override
    def create_config(self) -> ConexoConfig:
        return ConexoConfig(
            max_guesses=int(self._input_func("Max Guesses: ")),
            game_id=int(self._input_func("Game ID: ")),
        )

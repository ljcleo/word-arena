from collections.abc import Callable
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import ContextoFeedback, ContextoFinalResult, ContextoGuess
from ..formatters.base import ContextoFinalResultFormatter
from ..generators.common import ContextoConfig, get_contexto_game_count


class ContextoConfigGym[**P](
    BaseConfigGym[
        None, ContextoConfig, int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult, P
    ],
    ContextoFinalResultFormatter,
):
    pass


class ContextoExampleConfigGym(ContextoConfigGym):
    def __init__(
        self, *, log_func: Callable[[str], None], input_func: Callable[[str], str], **kwargs
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._input_func: Callable[[str], str] = input_func

    @override
    def create_config(self, *, meta_config: None) -> ContextoConfig:
        return ContextoConfig(
            max_guesses=int(self._input_func("Max Guesses: ")),
            game_id=int(self._input_func(f"Game ID (0--{get_contexto_game_count()}): ")),
        )

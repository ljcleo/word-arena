from collections.abc import Callable
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import ContextoFeedback, ContextoFinalResult, ContextoGuess
from ..formatters.base import ContextoFinalResultFormatter
from ..generators.common import ContextoConfig


class ContextoConfigGym[**P](
    BaseConfigGym[
        ContextoConfig, int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult, P
    ],
    ContextoFinalResultFormatter,
):
    def __init__(
        self,
        *,
        log_func: Callable[[str], None],
        config_creator: Callable[[], ContextoConfig],
        **kwargs,
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._config_creator: Callable[[], ContextoConfig] = config_creator

    @override
    def create_config(self) -> ContextoConfig:
        return self._config_creator()

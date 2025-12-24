from collections.abc import Callable
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import ContextoHintGuess
from ..formatters.base import ContextoHintFinalResultFormatter
from ..generators.common import ContextoHintConfig


class ContextoHintConfigGym[**P](
    BaseConfigGym[ContextoHintConfig, None, list[str], ContextoHintGuess, int, list[str], P],
    ContextoHintFinalResultFormatter,
):
    def __init__(
        self,
        *,
        log_func: Callable[[str], None],
        config_creator: Callable[[], ContextoHintConfig],
        **kwargs,
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._config_creator: Callable[[], ContextoHintConfig] = config_creator

    @override
    def create_config(self) -> ContextoHintConfig:
        return self._config_creator()

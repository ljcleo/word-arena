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
    def __init__(
        self,
        *,
        log_func: Callable[[str], None],
        config_creator: Callable[[], ConexoConfig],
        **kwargs,
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._config_creator: Callable[[], ConexoConfig] = config_creator

    @override
    def create_config(self) -> ConexoConfig:
        return self._config_creator()

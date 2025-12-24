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
    def __init__(
        self,
        *,
        log_func: Callable[[str], None],
        config_creator: Callable[[], LetrosoConfig],
        **kwargs,
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._config_creator: Callable[[], LetrosoConfig] = config_creator

    @override
    def create_config(self) -> LetrosoConfig:
        return self._config_creator()

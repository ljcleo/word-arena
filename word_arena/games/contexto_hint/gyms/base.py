from collections.abc import Callable
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import ContextoHintGuess
from ..formatters.base import ContextoHintFinalResultFormatter
from ..generators.common import ContextoHintConfig, ContextoHintMetaConfig


class ContextoHintConfigGym[**P](
    BaseConfigGym[
        ContextoHintMetaConfig,
        ContextoHintConfig,
        None,
        list[str],
        ContextoHintGuess,
        int,
        list[str],
        P,
    ],
    ContextoHintFinalResultFormatter,
):
    pass


class ContextoHintExampleConfigGym(ContextoHintConfigGym):
    def __init__(
        self, *, log_func: Callable[[str, str], None], input_func: Callable[[str], str], **kwargs
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._input_func: Callable[[str], str] = input_func

    @override
    def create_config(self, *, meta_config: ContextoHintMetaConfig) -> ContextoHintConfig:
        return ContextoHintConfig(
            num_candidates=int(self._input_func("Number of Candidates: ")),
            game_id=meta_config.select_game_id(
                selector=lambda n: int(self._input_func(f"Game ID (0--{n - 1}): "))
            ),
        )

from collections.abc import Callable
from typing import override

from .....common.config.reader.input import BaseInputConfigReader
from ...common import ContextoConfig
from ..common import ContextoMetaConfig


class ContextoInputConfigReader(BaseInputConfigReader[ContextoMetaConfig, ContextoConfig]):
    @override
    def input_config(
        self, *, meta_config: ContextoMetaConfig, input_func: Callable[[str], str]
    ) -> ContextoConfig:
        return ContextoConfig(
            base_url=meta_config.base_url,
            max_turns=int(input_func("Max Guesses: ")),
            game_id=meta_config.select_game_id(
                selector=lambda n: int(input_func(f"Game ID (0--{n - 1}): "))
            ),
        )

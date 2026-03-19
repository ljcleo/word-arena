from collections.abc import Callable
from typing import override

from .....common.config.reader.input import BaseInputConfigReader
from ...common import ContextoConfig
from ..utils import get_contexto_game_count


class ContextoInputConfigReader(BaseInputConfigReader[None, ContextoConfig]):
    @override
    def input_config(
        self, *, meta_config: None, input_func: Callable[[str], str]
    ) -> ContextoConfig:
        return ContextoConfig(
            max_turns=int(input_func("Max Guesses: ")),
            game_id=int(self._input_func(f"Game ID (0--{get_contexto_game_count() - 1}): ")),
        )

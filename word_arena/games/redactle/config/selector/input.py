from collections.abc import Callable
from typing import override

from .....common.config.selector.input import BaseInputConfigSelector
from ...common import RedactleConfig
from ..common import RedactleMetaConfig


class RedactleInputConfigSelector(BaseInputConfigSelector[RedactleMetaConfig, RedactleConfig]):
    @override
    def input_config(
        self, *, meta_config: RedactleMetaConfig, input_func: Callable[[str], str]
    ) -> RedactleConfig:
        return RedactleConfig(
            data_file=meta_config.data_file,
            stop_words=meta_config.stop_words,
            max_turns=int(input_func("Max Guesses: ")),
            game_id=meta_config.select_game_id(
                selector=lambda n: int(input_func(f"Game ID (0--{n - 1}): "))
            ),
        )

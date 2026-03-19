from collections.abc import Callable
from typing import override

from .....common.config.reader.input import BaseInputConfigReader
from ...common import ContextoHintConfig
from ..common import ContextoHintMetaConfig


class ContextoHintInputConfigReader(
    BaseInputConfigReader[ContextoHintMetaConfig, ContextoHintConfig]
):
    @override
    def input_config(
        self, *, meta_config: ContextoHintMetaConfig, input_func: Callable[[str], str]
    ) -> ContextoHintConfig:
        return ContextoHintConfig(
            data_file=meta_config.data_file,
            num_candidates=int(input_func("Number of Candidates: ")),
            game_id=meta_config.select_game_id(
                selector=lambda n: int(input_func(f"Game ID (0--{n - 1}): "))
            ),
        )

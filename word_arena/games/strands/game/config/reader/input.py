from collections.abc import Callable
from typing import override

from ......common.game.config.reader.input import BaseInputConfigReader
from ...common import StrandsConfig, StrandsMetaConfig


class StrandsInputConfigReader(BaseInputConfigReader[StrandsMetaConfig, StrandsConfig]):
    @override
    def input_config(
        self, *, meta_config: StrandsMetaConfig, input_func: Callable[[str], str]
    ) -> StrandsConfig:
        return StrandsConfig(
            data_file=meta_config.data_file,
            max_turns=int(input_func("Max Guesses: ")),
            game_id=meta_config.select_game_id(
                selector=lambda n: int(input_func(f"Game ID (0--{n - 1}): "))
            ),
        )

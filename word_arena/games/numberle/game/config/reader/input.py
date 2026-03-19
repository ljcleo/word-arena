from collections.abc import Callable
from typing import override

from ......common.game.config.reader.input import BaseInputConfigReader
from ...common import NumberleConfig, NumberleMetaConfig


class NumberleInputConfigReader(BaseInputConfigReader[NumberleMetaConfig, NumberleConfig]):
    @override
    def input_config(
        self, *, meta_config: NumberleMetaConfig, input_func: Callable[[str], str]
    ) -> NumberleConfig:
        eq_length: int = int(
            input_func(f"Equation Length ({'/'.join(map(str, meta_config.eq_length_pool))}): ")
        )

        return NumberleConfig(
            data_file=meta_config.data_file,
            eq_pool=meta_config.eq_pool,
            eq_length=eq_length,
            max_turns=int(input_func("Max Guesses: ")),
            game_ids=meta_config.select_game_ids(
                eq_length=eq_length,
                selector=lambda n: (
                    int(input_func(f"Equation ID {i + 1} (0--{n - 1}): "))
                    for i in range(int(input_func("Num Targets: ")))
                ),
            ),
        )

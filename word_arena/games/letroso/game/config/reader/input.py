from collections.abc import Callable
from typing import override

from ......common.game.config.reader.input import BaseInputConfigReader
from ...common import LetrosoConfig, LetrosoMetaConfig


class LetrosoInputConfigReader(BaseInputConfigReader[LetrosoMetaConfig, LetrosoConfig]):
    @override
    def input_config(
        self, *, meta_config: LetrosoMetaConfig, input_func: Callable[[str], str]
    ) -> LetrosoConfig:
        return LetrosoConfig(
            word_pool=meta_config.word_pool,
            max_letters=int(self._input_func("Max Input Letters: ")),
            max_turns=int(input_func("Max Guesses: ")),
            game_ids=meta_config.select_game_ids(
                selector=lambda n: (
                    int(input_func(f"Word ID {i + 1} (0--{n - 1}): "))
                    for i in range(int(input_func("Num Targets: ")))
                )
            ),
        )

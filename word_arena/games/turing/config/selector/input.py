from collections.abc import Callable
from typing import override

from .....common.config.selector.input import BaseInputConfigSelector
from ...common import TuringConfig
from ..common import TuringMetaConfig


class TuringInputConfigSelector(BaseInputConfigSelector[TuringMetaConfig, TuringConfig]):
    @override
    def input_config(
        self, *, meta_config: TuringMetaConfig, input_func: Callable[[str], str]
    ) -> TuringConfig:
        num_verifiers: int = int(
            input_func(
                f"Number of Verifiers ({'/'.join(map(str, meta_config.num_verifiers_pool))}): "
            )
        )

        return TuringConfig(
            data_file=meta_config.data_file,
            card_pool=meta_config.card_pool,
            num_verifiers=num_verifiers,
            max_turns=int(input_func("Max Guesses: ")),
            game_id=meta_config.select_game_id(
                num_verifiers=num_verifiers,
                selector=lambda n: int(input_func(f"Game ID (0--{n - 1}): ")),
            ),
        )

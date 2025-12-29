from collections.abc import Callable
from pathlib import Path
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo
from ..formatters.base import StrandsFinalResultFormatter
from ..generators.common import StrandsConfig, get_strands_game_count


class StrandsConfigGym[**P](
    BaseConfigGym[
        Path,
        StrandsConfig,
        StrandsInfo,
        None,
        StrandsGuess,
        StrandsFeedback,
        StrandsFinalResult,
        P,
    ],
    StrandsFinalResultFormatter,
):
    pass


class StrandsExampleConfigGym(StrandsConfigGym):
    def __init__(
        self, *, log_func: Callable[[str], None], input_func: Callable[[str], str], **kwargs
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._input_func: Callable[[str], str] = input_func

    @override
    def create_config(self, *, meta_config: Path) -> StrandsConfig:
        return StrandsConfig(
            max_guesses=int(self._input_func("Max Guesses: ")),
            game_id=int(
                self._input_func(
                    f"Game ID (0--{get_strands_game_count(data_file=meta_config) - 1}): "
                )
            ),
        )

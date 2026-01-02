from collections.abc import Callable
from pathlib import Path
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo
from ..generators.common import StrandsConfig, StrandsMetaConfig
from ..generators.provider import StrandsGameProvider
from ..players.manual import StrandsManualPlayer
from .base import StrandsConfigGym, StrandsExampleConfigGym


class StrandsManualGym(
    StrandsConfigGym[[Callable[[str], str], Callable[[str], None]]],
    BaseManualGym[
        StrandsMetaConfig,
        StrandsConfig,
        StrandsInfo,
        None,
        StrandsGuess,
        StrandsFeedback,
        StrandsFinalResult,
    ],
):
    def __init__(self, *, data_file: Path, log_func: Callable[[str], None], **kwargs) -> None:
        super().__init__(
            log_func=log_func,
            game_provider=StrandsGameProvider(meta_config=StrandsMetaConfig(data_file=data_file)),
            **kwargs,
        )

    @override
    def create_player(
        self, *, input_func: Callable[[str], str], player_log_func: Callable[[str], None]
    ) -> StrandsManualPlayer:
        return StrandsManualPlayer(input_func=input_func, player_log_func=player_log_func)


class StrandsExampleManualGym(StrandsExampleConfigGym, StrandsManualGym):
    def __init__(
        self, *, data_file: Path, log_func: Callable[[str], None], input_func: Callable[[str], str]
    ) -> None:
        super().__init__(data_file=data_file, log_func=log_func, input_func=input_func)

from collections.abc import Callable
from pathlib import Path
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import TuringFeedback, TuringFinalResult, TuringGuess, TuringInfo
from ..generators.common import TuringConfig, TuringMetaConfig
from ..generators.provider import TuringGameProvider
from ..players.manual import TuringManualPlayer
from .base import TuringConfigGym, TuringExampleConfigGym


class TuringManualGym(
    TuringConfigGym[[Callable[[str], str], Callable[[str, str], None]]],
    BaseManualGym[
        TuringMetaConfig,
        TuringConfig,
        TuringInfo,
        None,
        TuringGuess,
        TuringFeedback,
        TuringFinalResult,
    ],
):
    def __init__(self, *, data_file: Path, log_func: Callable[[str, str], None], **kwargs) -> None:
        super().__init__(
            log_func=log_func,
            game_provider=TuringGameProvider(meta_config=TuringMetaConfig(data_file=data_file)),
            **kwargs,
        )

    @override
    def create_player(
        self, *, input_func: Callable[[str], str], player_log_func: Callable[[str, str], None]
    ) -> TuringManualPlayer:
        return TuringManualPlayer(input_func=input_func, player_log_func=player_log_func)


class TuringExampleManualGym(TuringExampleConfigGym, TuringManualGym):
    def __init__(
        self,
        *,
        data_file: Path,
        log_func: Callable[[str, str], None],
        input_func: Callable[[str], str],
    ) -> None:
        super().__init__(data_file=data_file, log_func=log_func, input_func=input_func)

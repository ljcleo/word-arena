from collections.abc import Callable
from pathlib import Path
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo
from ..generators.common import WordleConfig, WordleMetaConfig
from ..generators.provider import WordleGameProvider
from ..players.manual import WordleManualPlayer
from .base import WordleConfigGym, WordleExampleConfigGym


class WordleManualGym(
    WordleConfigGym[[Callable[[str], str], Callable[[str, str], None]]],
    BaseManualGym[
        WordleMetaConfig,
        WordleConfig,
        WordleInfo,
        None,
        WordleGuess,
        WordleFeedback,
        WordleFinalResult,
    ],
):
    def __init__(self, *, data_file: Path, log_func: Callable[[str, str], None], **kwargs) -> None:
        super().__init__(
            log_func=log_func,
            game_provider=WordleGameProvider(meta_config=WordleMetaConfig(data_file=data_file)),
            **kwargs,
        )

    @override
    def create_player(
        self, *, input_func: Callable[[str], str], player_log_func: Callable[[str, str], None]
    ) -> WordleManualPlayer:
        return WordleManualPlayer(input_func=input_func, player_log_func=player_log_func)


class WordleExampleManualGym(WordleExampleConfigGym, WordleManualGym):
    def __init__(
        self,
        *,
        data_file: Path,
        log_func: Callable[[str, str], None],
        input_func: Callable[[str], str],
    ) -> None:
        super().__init__(data_file=data_file, log_func=log_func, input_func=input_func)

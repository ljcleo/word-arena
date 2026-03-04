from collections.abc import Callable
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import TuringFeedback, TuringFinalResult, TuringGuess, TuringInfo
from ..formatters.base import TuringFinalResultFormatter
from ..generators.common import TuringConfig, TuringMetaConfig


class TuringConfigGym[**P](
    BaseConfigGym[
        TuringMetaConfig,
        TuringConfig,
        TuringInfo,
        None,
        TuringGuess,
        TuringFeedback,
        TuringFinalResult,
        P,
    ],
    TuringFinalResultFormatter,
):
    pass


class TuringExampleConfigGym(TuringConfigGym):
    def __init__(
        self, *, log_func: Callable[[str], None], input_func: Callable[[str], str], **kwargs
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._input_func: Callable[[str], str] = input_func

    @override
    def create_config(self, *, meta_config: TuringMetaConfig) -> TuringConfig:
        num_verifiers: int = int(
            self._input_func(
                f"Number of Verifiers ({'/'.join(map(str, meta_config.num_verifiers_pool))}): "
            )
        )

        return TuringConfig(
            num_verifiers=num_verifiers,
            max_guesses=int(self._input_func("Max Guesses: ")),
            game_id=meta_config.select_game_id(
                num_verifiers=num_verifiers,
                selector=lambda n: int(self._input_func(f"Game ID (0--{n - 1}): ")),
            ),
        )

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
from ..common import (
    TuringFeedback,
    TuringFinalResult,
    TuringGuess,
    TuringInfo,
    TuringNote,
)
from ..generators.common import TuringConfig, TuringMetaConfig, TuringMutableMetaConfig
from ..generators.generator import TuringGameGenerator
from ..players.agent import TuringAgentPlayer
from .base import TuringConfigGym, TuringExampleConfigGym


class TuringAgentGym(
    TuringConfigGym[
        [
            BaseLLM,
            bool,
            TrainingConfig | None,
            Callable[[str, str], None],
            Callable[[str, str], None],
        ]
    ],
    BaseAgentGym[
        TuringMetaConfig,
        TuringMutableMetaConfig,
        TuringConfig,
        TuringInfo,
        None,
        TuringGuess,
        TuringFeedback,
        TuringFinalResult,
        TuringNote,
    ],
):
    def __init__(
        self,
        *,
        data_file: Path,
        mutable_meta_config_pool: Iterable[TuringMutableMetaConfig],
        seed: int,
        log_func: Callable[[str, str], None],
        **kwargs,
    ) -> None:
        super().__init__(
            log_func=log_func,
            game_generator=TuringGameGenerator(
                meta_config=TuringMetaConfig(data_file=data_file),
                mutable_meta_config_pool=mutable_meta_config_pool,
                seed=seed,
            ),
            **kwargs,
        )

    @override
    def create_player(
        self,
        *,
        model: BaseLLM,
        do_analyze: bool,
        player_log_func: Callable[[str, str], None],
        agent_log_func: Callable[[str, str], None],
    ) -> TuringAgentPlayer:
        return TuringAgentPlayer(
            model=model,
            do_analyze=do_analyze,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )


class TuringExampleAgentGym(TuringExampleConfigGym, TuringAgentGym):
    def __init__(
        self,
        *,
        data_file: Path,
        mutable_meta_config_pool: Iterable[TuringMutableMetaConfig],
        seed: int,
        log_func: Callable[[str, str], None],
        input_func: Callable[[str], str],
    ) -> None:
        super().__init__(
            data_file=data_file,
            mutable_meta_config_pool=mutable_meta_config_pool,
            seed=seed,
            log_func=log_func,
            input_func=input_func,
        )

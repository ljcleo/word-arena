from collections.abc import Callable, Iterable
from pathlib import Path
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
from ..common import (
    StrandsFeedback,
    StrandsFinalResult,
    StrandsGuess,
    StrandsInfo,
    StrandsNote,
)
from ..generators.common import StrandsConfig, StrandsMetaConfig
from ..generators.generator import StrandsGameGenerator
from ..players.agent import StrandsAgentPlayer
from .base import StrandsConfigGym, StrandsExampleConfigGym


class StrandsAgentGym(
    StrandsConfigGym[
        [BaseLLM, bool, TrainingConfig | None, Callable[[str], None], Callable[[str], None]]
    ],
    BaseAgentGym[
        StrandsMetaConfig,
        int,
        StrandsConfig,
        StrandsInfo,
        None,
        StrandsGuess,
        StrandsFeedback,
        StrandsFinalResult,
        StrandsNote,
    ],
):
    def __init__(
        self,
        *,
        data_file: Path,
        mutable_meta_config_pool: Iterable[int],
        seed: int,
        log_func: Callable[[str], None],
        **kwargs,
    ) -> None:
        super().__init__(
            log_func=log_func,
            game_generator=StrandsGameGenerator(
                meta_config=StrandsMetaConfig(data_file=data_file),
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
        player_log_func: Callable[[str], None],
        agent_log_func: Callable[[str], None],
    ) -> StrandsAgentPlayer:
        return StrandsAgentPlayer(
            model=model,
            do_analyze=do_analyze,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )


class StrandsExampleAgentGym(StrandsExampleConfigGym, StrandsAgentGym):
    def __init__(
        self,
        *,
        data_file: Path,
        mutable_meta_config_pool: Iterable[int],
        seed: int,
        log_func: Callable[[str], None],
        input_func: Callable[[str], str],
    ) -> None:
        super().__init__(
            data_file=data_file,
            mutable_meta_config_pool=mutable_meta_config_pool,
            seed=seed,
            log_func=log_func,
            input_func=input_func,
        )

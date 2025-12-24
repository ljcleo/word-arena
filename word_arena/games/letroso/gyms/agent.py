from collections.abc import Callable, Iterable
from pathlib import Path
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
from ..common import (
    LetrosoExperience,
    LetrosoFeedback,
    LetrosoFinalResult,
    LetrosoGuess,
    LetrosoInfo,
)
from ..generators.common import LetrosoConfig, LetrosoMetaConfig, LetrosoMutableMetaConfig
from ..generators.generator import LetrosoGameGenerator
from ..players.agent import LetrosoAgentPlayer
from .base import LetrosoConfigGym


class LetrosoAgentGym(
    LetrosoConfigGym[
        [BaseLLM, bool, TrainingConfig | None, Callable[[str], None], Callable[[str], None]]
    ],
    BaseAgentGym[
        LetrosoMetaConfig,
        LetrosoMutableMetaConfig,
        LetrosoConfig,
        LetrosoInfo,
        None,
        LetrosoGuess,
        LetrosoFeedback,
        LetrosoFinalResult,
        LetrosoExperience,
    ],
):
    def __init__(
        self,
        *,
        data_file: Path,
        mutable_meta_config_pool: Iterable[LetrosoMutableMetaConfig],
        seed: int,
        log_func: Callable[[str], None],
        config_creator: Callable[[], LetrosoConfig],
    ) -> None:
        super().__init__(
            log_func=log_func,
            config_creator=config_creator,
            game_generator=LetrosoGameGenerator(
                data_file=data_file, mutable_meta_config_pool=mutable_meta_config_pool, seed=seed
            ),
        )

    @override
    def create_player(
        self,
        *,
        model: BaseLLM,
        do_analyze: bool,
        player_log_func: Callable[[str], None],
        agent_log_func: Callable[[str], None],
    ) -> LetrosoAgentPlayer:
        return LetrosoAgentPlayer(
            model=model,
            do_analyze=do_analyze,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

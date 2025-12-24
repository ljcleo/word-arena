from collections.abc import Callable, Iterable
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
from ..common import ContextoExperience, ContextoFeedback, ContextoFinalResult, ContextoGuess
from ..generators.common import ContextoConfig
from ..generators.generator import ContextoGameGenerator
from ..players.agent import ContextoAgentPlayer
from .base import ContextoConfigGym


class ContextoAgentGym(
    ContextoConfigGym[
        [BaseLLM, bool, TrainingConfig | None, Callable[[str], None], Callable[[str], None]]
    ],
    BaseAgentGym[
        None,
        int,
        ContextoConfig,
        int,
        None,
        ContextoGuess,
        ContextoFeedback,
        ContextoFinalResult,
        ContextoExperience,
    ],
):
    def __init__(
        self,
        *,
        mutable_meta_config_pool: Iterable[int],
        seed: int,
        log_func: Callable[[str], None],
        config_creator: Callable[[], ContextoConfig],
    ) -> None:
        super().__init__(
            log_func=log_func,
            config_creator=config_creator,
            game_generator=ContextoGameGenerator(
                mutable_meta_config_pool=mutable_meta_config_pool, seed=seed
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
    ) -> ContextoAgentPlayer:
        return ContextoAgentPlayer(
            model=model,
            do_analyze=do_analyze,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

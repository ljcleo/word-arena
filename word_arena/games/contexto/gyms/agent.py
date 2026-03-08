from collections.abc import Callable, Iterable
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
from ..common import ContextoFeedback, ContextoFinalResult, ContextoGuess, ContextoNote
from ..generators.common import ContextoConfig
from ..generators.generator import ContextoGameGenerator
from ..players.agent import ContextoAgentPlayer
from .base import ContextoConfigGym, ContextoExampleConfigGym


class ContextoAgentGym(
    ContextoConfigGym[
        [
            BaseLLM,
            bool,
            TrainingConfig | None,
            Callable[[str, str], None],
            Callable[[str, str], None],
        ]
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
        ContextoNote,
    ],
):
    def __init__(
        self,
        *,
        mutable_meta_config_pool: Iterable[int],
        seed: int,
        log_func: Callable[[str, str], None],
        **kwargs,
    ) -> None:
        super().__init__(
            log_func=log_func,
            game_generator=ContextoGameGenerator(
                meta_config=None, mutable_meta_config_pool=mutable_meta_config_pool, seed=seed
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
    ) -> ContextoAgentPlayer:
        return ContextoAgentPlayer(
            model=model,
            do_analyze=do_analyze,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )


class ContextoExampleAgentGym(ContextoExampleConfigGym, ContextoAgentGym):
    def __init__(
        self,
        *,
        mutable_meta_config_pool: Iterable[int],
        seed: int,
        log_func: Callable[[str, str], None],
        input_func: Callable[[str], str],
    ) -> None:
        super().__init__(
            mutable_meta_config_pool=mutable_meta_config_pool,
            seed=seed,
            log_func=log_func,
            input_func=input_func,
        )

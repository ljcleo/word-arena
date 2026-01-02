from collections.abc import Callable, Iterable
from pathlib import Path
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
from ..common import (
    ConnectionsFeedback,
    ConnectionsFinalResult,
    ConnectionsGuess,
    ConnectionsInfo,
    ConnectionsNote,
)
from ..generators.common import ConnectionsConfig, ConnectionsMetaConfig
from ..generators.generator import ConnectionsGameGenerator
from ..players.agent import ConnectionsAgentPlayer
from .base import ConnectionsConfigGym, ConnectionsExampleConfigGym


class ConnectionsAgentGym(
    ConnectionsConfigGym[
        [BaseLLM, bool, TrainingConfig | None, Callable[[str], None], Callable[[str], None]]
    ],
    BaseAgentGym[
        ConnectionsMetaConfig,
        int,
        ConnectionsConfig,
        ConnectionsInfo,
        None,
        ConnectionsGuess,
        ConnectionsFeedback,
        ConnectionsFinalResult,
        ConnectionsNote,
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
            game_generator=ConnectionsGameGenerator(
                meta_config=ConnectionsMetaConfig(data_file=data_file),
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
    ) -> ConnectionsAgentPlayer:
        return ConnectionsAgentPlayer(
            model=model,
            do_analyze=do_analyze,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )


class ConnectionsExampleAgentGym(ConnectionsExampleConfigGym, ConnectionsAgentGym):
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

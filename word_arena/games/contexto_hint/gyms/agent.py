from collections.abc import Callable, Iterable
from pathlib import Path
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
from ..common import ContextoHintExperience, ContextoHintGuess
from ..generators.common import ContextoHintConfig
from ..generators.generator import ContextoHintGameGenerator
from ..players.agent import ContextoHintAgentPlayer
from .base import ContextoHintConfigGym


class ContextoHintAgentGym(
    ContextoHintConfigGym[
        [BaseLLM, bool, TrainingConfig | None, Callable[[str], None], Callable[[str], None]]
    ],
    BaseAgentGym[
        Path,
        int,
        ContextoHintConfig,
        None,
        list[str],
        ContextoHintGuess,
        int,
        list[str],
        ContextoHintExperience,
    ],
):
    def __init__(
        self,
        *,
        data_file: Path,
        mutable_meta_config_pool: Iterable[int],
        seed: int,
        log_func: Callable[[str], None],
        config_creator: Callable[[], ContextoHintConfig],
    ) -> None:
        super().__init__(
            game_generator=ContextoHintGameGenerator(
                data_file=data_file, mutable_meta_config_pool=mutable_meta_config_pool, seed=seed
            ),
            log_func=log_func,
            config_creator=config_creator,
        )

    @override
    def create_player(
        self,
        *,
        model: BaseLLM,
        do_analyze: bool,
        player_log_func: Callable[[str], None],
        agent_log_func: Callable[[str], None],
    ) -> ContextoHintAgentPlayer:
        return ContextoHintAgentPlayer(
            model=model,
            do_analyze=do_analyze,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

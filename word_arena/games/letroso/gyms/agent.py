from collections.abc import Callable, Iterable
from pathlib import Path
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
from ..common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo, LetrosoNote
from ..generators.common import LetrosoConfig, LetrosoMetaConfig, LetrosoMutableMetaConfig
from ..generators.generator import LetrosoGameGenerator
from ..players.agent import LetrosoAgentPlayer
from .base import LetrosoConfigGym, LetrosoExampleConfigGym


class LetrosoAgentGym(
    LetrosoConfigGym[
        [
            BaseLLM,
            bool,
            TrainingConfig | None,
            Callable[[str, str], None],
            Callable[[str, str], None],
        ]
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
        LetrosoNote,
    ],
):
    def __init__(
        self,
        *,
        data_file: Path,
        mutable_meta_config_pool: Iterable[LetrosoMutableMetaConfig],
        seed: int,
        log_func: Callable[[str, str], None],
        **kwargs,
    ) -> None:
        super().__init__(
            log_func=log_func,
            game_generator=LetrosoGameGenerator(
                meta_config=LetrosoMetaConfig(data_file=data_file),
                mutable_meta_config_pool=mutable_meta_config_pool,
                seed=seed,
            ),
        )

    @override
    def create_player(
        self,
        *,
        model: BaseLLM,
        do_analyze: bool,
        player_log_func: Callable[[str, str], None],
        agent_log_func: Callable[[str, str], None],
    ) -> LetrosoAgentPlayer:
        return LetrosoAgentPlayer(
            model=model,
            do_analyze=do_analyze,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )


class LetrosoExampleAgentGym(LetrosoExampleConfigGym, LetrosoAgentGym):
    def __init__(
        self,
        *,
        data_file: Path,
        mutable_meta_config_pool: Iterable[LetrosoMutableMetaConfig],
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

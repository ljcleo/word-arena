from collections.abc import Callable, Iterable
from pathlib import Path
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
from ..common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo, WordleNote
from ..generators.common import WordleConfig, WordleMetaConfig, WordleMutableMetaConfig
from ..generators.generator import WordleGameGenerator
from ..players.agent import WordleAgentPlayer
from .base import WordleConfigGym, WordleExampleConfigGym


class WordleAgentGym(
    WordleConfigGym[
        [
            BaseLLM,
            bool,
            TrainingConfig | None,
            Callable[[str, str], None],
            Callable[[str, str], None],
        ]
    ],
    BaseAgentGym[
        WordleMetaConfig,
        WordleMutableMetaConfig,
        WordleConfig,
        WordleInfo,
        None,
        WordleGuess,
        WordleFeedback,
        WordleFinalResult,
        WordleNote,
    ],
):
    def __init__(
        self,
        *,
        data_file: Path,
        mutable_meta_config_pool: Iterable[WordleMutableMetaConfig],
        seed: int,
        log_func: Callable[[str, str], None],
        **kwargs,
    ) -> None:
        super().__init__(
            log_func=log_func,
            game_generator=WordleGameGenerator(
                meta_config=WordleMetaConfig(data_file=data_file),
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
    ) -> WordleAgentPlayer:
        return WordleAgentPlayer(
            model=model,
            do_analyze=do_analyze,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )


class WordleExampleAgentGym(WordleExampleConfigGym, WordleAgentGym):
    def __init__(
        self,
        *,
        data_file: Path,
        mutable_meta_config_pool: Iterable[WordleMutableMetaConfig],
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

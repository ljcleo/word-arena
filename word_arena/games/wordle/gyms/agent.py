from collections.abc import Callable, Iterable
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
from ..common import (
    WordleExperience,
    WordleFeedback,
    WordleFinalResult,
    WordleGuess,
    WordleInfo,
)
from ..generators.common import WordleConfig, WordleSetting
from ..generators.generator import WordleGameGenerator
from ..players.agent import WordleAgentPlayer
from .base import WordleConfigGym


class WordleAgentGym(
    BaseAgentGym[
        WordleSetting,
        WordleConfig,
        WordleInfo,
        None,
        WordleGuess,
        WordleFeedback,
        WordleFinalResult,
        WordleExperience,
    ],
    WordleConfigGym[
        [BaseLLM, bool, TrainingConfig | None, Callable[[str], None], Callable[[str], None]]
    ],
):
    def __init__(
        self,
        *,
        setting_pool: Iterable[WordleSetting],
        seed: int,
        word_list: Iterable[str],
        game_word_list: Iterable[str],
        create_config_func: Callable[[], WordleConfig],
        log_func: Callable[[str], None],
    ) -> None:
        super().__init__(
            game_generator=WordleGameGenerator(
                setting_pool=setting_pool,
                seed=seed,
                word_list=word_list,
                game_word_list=game_word_list,
            ),
            create_config_func=create_config_func,
            log_func=log_func,
        )

    @override
    def create_player(
        self,
        *,
        model: BaseLLM,
        do_analyze: bool,
        player_log_func: Callable[[str], None],
        agent_log_func: Callable[[str], None],
    ) -> WordleAgentPlayer:
        return WordleAgentPlayer(
            model=model,
            do_analyze=do_analyze,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

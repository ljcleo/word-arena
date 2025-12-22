from collections.abc import Iterable
from pathlib import Path
from typing import override

from ....common.gym.agent import BaseAgentGym
from ....common.llm.base import BaseLLM
from ....common.player.agent.common import PromptMode
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
    WordleConfigGym[[BaseLLM, PromptMode]],
):
    def __init__(
        self, *, setting_pool: Iterable[WordleSetting], seed: int, word_list_file: Path
    ) -> None:
        super().__init__(
            game_generator=WordleGameGenerator(
                setting_pool=setting_pool, seed=seed, word_list_file=word_list_file
            )
        )

        super(BaseAgentGym, self).__init__(word_list_file=word_list_file)

    @override
    def create_player(self, *, model: BaseLLM, prompt_mode: PromptMode) -> WordleAgentPlayer:
        return WordleAgentPlayer(model=model, prompt_mode=prompt_mode)

from collections.abc import Iterable
from pathlib import Path
from typing import override

from ....common.gym.agent import BaseAgentGym
from ....common.llm.base import BaseLLM
from ....common.player.agent.common import PromptMode
from ..common import (
    LetrosoExperience,
    LetrosoFeedback,
    LetrosoFinalResult,
    LetrosoGuess,
    LetrosoInfo,
)
from ..generators.common import LetrosoConfig, LetrosoSetting
from ..generators.generator import LetrosoGameGenerator
from ..players.agent import LetrosoAgentPlayer
from .base import LetrosoConfigGym


class LetrosoAgentGym(
    BaseAgentGym[
        LetrosoSetting,
        LetrosoConfig,
        LetrosoInfo,
        None,
        LetrosoGuess,
        LetrosoFeedback,
        LetrosoFinalResult,
        LetrosoExperience,
    ],
    LetrosoConfigGym[[BaseLLM, PromptMode]],
):
    def __init__(
        self, *, setting_pool: Iterable[LetrosoSetting], seed: int, word_list_file: Path
    ) -> None:
        super().__init__(
            game_generator=LetrosoGameGenerator(
                setting_pool=setting_pool, seed=seed, word_list_file=word_list_file
            )
        )

        super(BaseAgentGym, self).__init__(word_list_file=word_list_file)

    @override
    def create_player(self, *, model: BaseLLM, prompt_mode: PromptMode) -> LetrosoAgentPlayer:
        return LetrosoAgentPlayer(model=model, prompt_mode=prompt_mode)

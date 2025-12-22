from collections.abc import Iterable
from pathlib import Path
from typing import override

from ....common.gym.agent import BaseAgentGym
from ....common.llm.base import BaseLLM
from ....common.player.agent.common import PromptMode
from ..common import ContextoHintExperience, ContextoHintGuess
from ..generators.common import ContextoHintConfig, ContextoHintSetting
from ..generators.generator import ContextoHintGameGenerator
from ..players.agent import ContextoHintAgentPlayer
from .base import ContextoHintConfigGym


class ContextoHintAgentGym(
    BaseAgentGym[
        ContextoHintSetting,
        ContextoHintConfig,
        None,
        list[str],
        ContextoHintGuess,
        int,
        list[str],
        ContextoHintExperience,
    ],
    ContextoHintConfigGym[[BaseLLM, PromptMode]],
):
    def __init__(
        self, *, setting_pool: Iterable[ContextoHintSetting], seed: int, games_dir: Path
    ) -> None:
        super().__init__(
            game_generator=ContextoHintGameGenerator(
                setting_pool=setting_pool, seed=seed, games_dir=games_dir
            )
        )

    @override
    def create_player(self, *, model: BaseLLM, prompt_mode: PromptMode) -> ContextoHintAgentPlayer:
        return ContextoHintAgentPlayer(model=model, prompt_mode=prompt_mode)

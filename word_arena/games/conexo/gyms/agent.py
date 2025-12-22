from collections.abc import Iterable
from pathlib import Path
from typing import override

from ....common.gym.agent import BaseAgentGym
from ....common.llm.base import BaseLLM
from ....common.player.agent.common import PromptMode
from ..common import ConexoExperience, ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo
from ..generators.common import ConexoConfig, ConexoSetting
from ..generators.generator import ConexoGameGenerator
from ..players.agent import ConexoAgentPlayer
from .base import ConexoConfigGym


class ConexoAgentGym(
    BaseAgentGym[
        ConexoSetting,
        ConexoConfig,
        ConexoInfo,
        None,
        ConexoGuess,
        ConexoFeedback,
        ConexoFinalResult,
        ConexoExperience,
    ],
    ConexoConfigGym[[BaseLLM, PromptMode]],
):
    def __init__(
        self, *, setting_pool: Iterable[ConexoSetting], seed: int, games_dir: Path
    ) -> None:
        super().__init__(
            game_generator=ConexoGameGenerator(
                setting_pool=setting_pool, seed=seed, games_dir=games_dir
            )
        )

    @override
    def create_player(self, *, model: BaseLLM, prompt_mode: PromptMode) -> ConexoAgentPlayer:
        return ConexoAgentPlayer(model=model, prompt_mode=prompt_mode)

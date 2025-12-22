from collections.abc import Iterable
from typing import override

from ....common.gym.agent import BaseAgentGym
from ....common.llm.base import BaseLLM
from ....common.player.agent.common import PromptMode
from ..common import ContextoExperience, ContextoFeedback, ContextoFinalResult, ContextoGuess
from ..generators.common import ContextoConfig, ContextoSetting
from ..generators.generator import ContextoGameGenerator
from ..players.agent import ContextoAgentPlayer
from .base import ContextoConfigGym


class ContextoAgentGym(
    BaseAgentGym[
        ContextoSetting,
        ContextoConfig,
        int,
        None,
        ContextoGuess,
        ContextoFeedback,
        ContextoFinalResult,
        ContextoExperience,
    ],
    ContextoConfigGym[[BaseLLM, PromptMode]],
):
    def __init__(self, *, setting_pool: Iterable[ContextoSetting], seed: int) -> None:
        super().__init__(game_generator=ContextoGameGenerator(setting_pool=setting_pool, seed=seed))

    @override
    def create_player(self, *, model: BaseLLM, prompt_mode: PromptMode) -> ContextoAgentPlayer:
        return ContextoAgentPlayer(model=model, prompt_mode=prompt_mode)

from collections.abc import Callable, Iterable
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
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
    ContextoConfigGym[[BaseLLM, bool, TrainingConfig | None]],
):
    def __init__(
        self,
        *,
        setting_pool: Iterable[ContextoSetting],
        seed: int,
        create_config_func: Callable[[], ContextoConfig],
    ) -> None:
        super().__init__(
            game_generator=ContextoGameGenerator(setting_pool=setting_pool, seed=seed),
            create_config_func=create_config_func,
        )

    @override
    def create_player(self, *, model: BaseLLM, do_analyze: bool) -> ContextoAgentPlayer:
        return ContextoAgentPlayer(model=model, do_analyze=do_analyze)

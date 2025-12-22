from collections.abc import Callable, Iterable
from pathlib import Path
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
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
    ConexoConfigGym[[BaseLLM, bool, TrainingConfig | None]],
):
    def __init__(
        self,
        *,
        setting_pool: Iterable[ConexoSetting],
        seed: int,
        games_dir: Path,
        create_config_func: Callable[[], ConexoConfig],
    ) -> None:
        super().__init__(
            game_generator=ConexoGameGenerator(
                setting_pool=setting_pool, seed=seed, games_dir=games_dir
            ),
            create_config_func=create_config_func,
        )

    @override
    def create_player(self, *, model: BaseLLM, do_analyze: bool) -> ConexoAgentPlayer:
        return ConexoAgentPlayer(model=model, do_analyze=do_analyze)

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
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
    ContextoHintConfigGym[[BaseLLM, bool, TrainingConfig | None]],
):
    def __init__(
        self,
        *,
        setting_pool: Iterable[ContextoHintSetting],
        seed: int,
        games_dir: Path,
        create_config_func: Callable[[], ContextoHintConfig],
    ) -> None:
        super().__init__(
            game_generator=ContextoHintGameGenerator(
                setting_pool=setting_pool, seed=seed, games_dir=games_dir
            ),
            create_config_func=create_config_func,
        )

    @override
    def create_player(self, *, model: BaseLLM, do_analyze: bool) -> ContextoHintAgentPlayer:
        return ContextoHintAgentPlayer(model=model, do_analyze=do_analyze)

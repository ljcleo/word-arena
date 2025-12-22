from collections.abc import Callable, Iterable
from typing import override

from ....common.gym.agent.common import TrainingConfig
from ....common.gym.agent.gym import BaseAgentGym
from ....common.llm.base import BaseLLM
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
    LetrosoConfigGym[[BaseLLM, bool, TrainingConfig | None]],
):
    def __init__(
        self,
        *,
        setting_pool: Iterable[LetrosoSetting],
        seed: int,
        word_list: Iterable[str],
        create_config_func: Callable[[], LetrosoConfig],
    ) -> None:
        super().__init__(
            game_generator=LetrosoGameGenerator(
                setting_pool=setting_pool, seed=seed, word_list=word_list
            ),
            create_config_func=create_config_func,
        )

    @override
    def create_player(self, *, model: BaseLLM, do_analyze: bool) -> LetrosoAgentPlayer:
        return LetrosoAgentPlayer(model=model, do_analyze=do_analyze)

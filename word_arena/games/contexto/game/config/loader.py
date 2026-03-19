from random import Random
from typing import override

from .....common.game.config.loader.base import BaseConfigLoader
from ..common import ContextoConfig
from .utils import get_contexto_game_count


class ContextoConfigLoader(BaseConfigLoader[None, int, ContextoConfig]):
    @override
    def build_config(
        self, *, meta_config: None, mutable_meta_config: int, rng: Random
    ) -> ContextoConfig:
        return ContextoConfig(
            max_turns=mutable_meta_config, game_id=rng.randrange(get_contexto_game_count())
        )

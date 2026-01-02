from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import LetrosoGame
from .common import LetrosoConfig, LetrosoMetaConfig, LetrosoMutableMetaConfig
from .provider import LetrosoGameProvider


class LetrosoGameGenerator(
    LetrosoGameProvider,
    BaseGameGenerator[LetrosoMetaConfig, LetrosoMutableMetaConfig, LetrosoConfig, LetrosoGame],
):
    @override
    def generate_config(
        self,
        *,
        meta_config: LetrosoMetaConfig,
        mutable_meta_config: LetrosoMutableMetaConfig,
        rng: Random,
    ) -> LetrosoConfig:
        return LetrosoConfig(
            max_letters=mutable_meta_config.max_letters,
            max_guesses=mutable_meta_config.max_guesses,
            game_ids=meta_config.random_game_ids(count=mutable_meta_config.num_targets, rng=rng),
        )

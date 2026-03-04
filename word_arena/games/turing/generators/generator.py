from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import TuringGame
from .common import TuringConfig, TuringMetaConfig, TuringMutableMetaConfig
from .provider import TuringGameProvider


class TuringGameGenerator(
    TuringGameProvider,
    BaseGameGenerator[TuringMetaConfig, TuringMutableMetaConfig, TuringConfig, TuringGame],
):
    @override
    def generate_config(
        self,
        *,
        meta_config: TuringMetaConfig,
        mutable_meta_config: TuringMutableMetaConfig,
        rng: Random,
    ) -> TuringConfig:
        return TuringConfig(
            num_verifiers=mutable_meta_config.num_verifiers,
            max_guesses=mutable_meta_config.max_guesses,
            game_id=meta_config.random_game_id(
                num_verifiers=mutable_meta_config.num_verifiers, rng=rng
            ),
        )

from random import Random
from typing import override

from ....common.config.generator.base import BaseConfigGenerator
from ..common import TuringConfig
from .common import TuringMetaConfig, TuringMutableMetaConfig


class TuringConfigGenerator(
    BaseConfigGenerator[TuringMetaConfig, TuringMutableMetaConfig, TuringConfig]
):
    @override
    def __call__(
        self,
        *,
        meta_config: TuringMetaConfig,
        mutable_meta_config: TuringMutableMetaConfig,
        rng: Random,
    ) -> TuringConfig:
        return TuringConfig(
            data_file=meta_config.data_file,
            card_pool=meta_config.card_pool,
            num_verifiers=mutable_meta_config.num_verifiers,
            max_turns=mutable_meta_config.max_turns,
            game_id=meta_config.random_game_id(
                num_verifiers=mutable_meta_config.num_verifiers, rng=rng
            ),
        )

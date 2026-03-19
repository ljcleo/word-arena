from random import Random
from typing import override

from ....common.config.loader.base import BaseConfigLoader
from ..common import TuringConfig
from .common import TuringMetaConfig, TuringMutableMetaConfig


class TuringConfigLoader(BaseConfigLoader[TuringMetaConfig, TuringMutableMetaConfig, TuringConfig]):
    @override
    def build_config(
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

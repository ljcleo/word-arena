from collections.abc import Sequence
from random import Random
from typing import Any

from ..config.generator.base import BaseConfigGenerator
from ..config.reader.base import BaseConfigReader
from ..game.engine.base import BaseGameEngine
from ..game.game import Game
from ..game.renderer.base import BaseGameRenderer
from ..player.player import Player
from .common import TrainingConfig


class Gym[MT, UT, CT, IT, GT, FT, RT]:
    def __init__(
        self,
        *,
        meta_config: MT,
        mutable_meta_config_pool: Sequence[UT],
        config_reader: BaseConfigReader[MT, CT],
        config_generator: BaseConfigGenerator[MT, UT, CT],
        game_engine_cls: type[BaseGameEngine[CT, IT, GT, FT, RT]],
        game_renderer: BaseGameRenderer[IT, GT, FT, RT],
    ) -> None:
        self._meta_config: MT = meta_config
        self._mutable_meta_config_pool: Sequence[UT] = mutable_meta_config_pool
        self._config_reader: BaseConfigReader[MT, CT] = config_reader
        self._config_generator: BaseConfigGenerator[MT, UT, CT] = config_generator
        self._game_engine_cls: type[BaseGameEngine[CT, IT, GT, FT, RT]] = game_engine_cls
        self._game_renderer: BaseGameRenderer[IT, GT, FT, RT] = game_renderer

    def play(self, *, player: Player[Any, IT, Any, GT, FT, RT, Any]) -> None:
        player.play(game=self._load_game(config=self._read_config()))

    def train(
        self, *, player: Player[Any, IT, Any, GT, FT, RT, Any], training_config: TrainingConfig
    ) -> None:
        rng: Random = Random(x=training_config.seed)

        for _ in range(training_config.num_train_loops):
            for _ in range(training_config.num_in_loop_trials):
                player.play(game=self._load_game(config=self._generate_config(rng=rng)))
            else:
                player.evolve()

    def _load_game(self, *, config: CT) -> Game[IT, GT, FT, RT]:
        return Game(engine=self._game_engine_cls(config=config), renderer=self._game_renderer)

    def _read_config(self) -> CT:
        return self._config_reader(meta_config=self._meta_config)

    def _generate_config(self, *, rng: Random) -> CT:
        return self._config_generator(
            meta_config=self._meta_config,
            mutable_meta_config=rng.choice(self._mutable_meta_config_pool),
            rng=rng,
        )

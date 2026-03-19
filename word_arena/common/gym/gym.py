from random import Random

from ..game.config.loader.base import BaseConfigLoader
from ..game.game import Game
from ..game.loader.base import BaseGameLoader
from ..player.base import BasePlayer
from .common import TrainingConfig


class Gym[MT, UT, CT, IT, GT, FT, RT]:
    def __init__(
        self,
        *,
        config_loader: BaseConfigLoader[MT, UT, CT],
        game_loader: BaseGameLoader[CT, IT, GT, FT, RT],
    ) -> None:
        self._config_loader: BaseConfigLoader[MT, UT, CT] = config_loader
        self._game_loader: BaseGameLoader[CT, IT, GT, FT, RT] = game_loader

    def play(self, *, player: BasePlayer[IT, GT, FT, RT]) -> None:
        player.play(game=self._load_game(rng=None))

    def train(self, *, player: BasePlayer[IT, GT, FT, RT], training_config: TrainingConfig) -> None:
        rng: Random = Random(x=training_config.seed)

        for _ in range(training_config.num_train_loops):
            for _ in range(training_config.num_in_loop_trials):
                player.play(game=self._load_game(rng=rng))
            else:
                player.evolve()

    def _load_game(self, *, rng: Random | None) -> Game[IT, GT, FT, RT]:
        return self._game_loader.load_game(
            config=self._config_loader.load_config()
            if rng is None
            else self._config_loader.load_random_config(rng=rng)
        )

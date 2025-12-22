from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override

from pydantic import BaseModel

from ..game.base import BaseGame
from ..game.common import GameRecord
from ..generator.generator import BaseGameGenerator
from ..llm.base import BaseLLM
from ..player.agent.player import BaseAgentPlayer
from .base import BaseConfigGym


class BaseAgentGym[ST, CT, IT, HT, GT: BaseModel, FT, RT, ET: BaseModel](
    BaseConfigGym[CT, IT, HT, GT, FT, RT, [BaseLLM, bool]], ABC
):
    def __init__(
        self, *, game_generator: BaseGameGenerator[ST, CT, BaseGame[IT, HT, GT, FT, RT]]
    ) -> None:
        self._game_generator: BaseGameGenerator[ST, CT, BaseGame[IT, HT, GT, FT, RT]] = (
            game_generator
        )

    @override
    def create_player_with_cb(
        self, model: BaseLLM, do_analyze: bool
    ) -> tuple[
        BaseAgentPlayer[IT, HT, GT, FT, ET],
        Callable[[], None],
        Callable[[GameRecord[IT, HT, GT, FT, RT]], None],
    ]:
        player: BaseAgentPlayer[IT, HT, GT, FT, ET] = self.create_player(
            model=model, do_analyze=do_analyze
        )

        def prepare_player() -> None:
            if input("Train? (y/n): ")[0].lower() == "y":
                num_train_loops: int = int(input("Number of Train Loops: "))
                num_in_loop_trials: int = int(input("Number of In-loop Trials: "))

                for _ in range(num_train_loops):
                    for i in range(num_in_loop_trials):
                        player.memory.reflect(
                            game_record=self._game_generator.random_game().play(player=player),
                            update_experience=i == num_in_loop_trials - 1,
                        )

        def summarize_player(game_record: GameRecord[IT, HT, GT, FT, RT]) -> None:
            player.memory.reflect(game_record=game_record, update_experience=False)

        return player, prepare_player, summarize_player

    @override
    def create_game_from_config(self, *, config: CT) -> BaseGame[IT, HT, GT, FT, RT]:
        return self._game_generator.create_game(config=config)

    @abstractmethod
    def create_player(
        self, *, model: BaseLLM, do_analyze: bool
    ) -> BaseAgentPlayer[IT, HT, GT, FT, ET]:
        raise NotImplementedError()

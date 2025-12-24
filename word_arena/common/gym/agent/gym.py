from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override

from pydantic import BaseModel

from ...game.base import BaseGame
from ...game.common import GameRecord
from ...generator.generator import BaseGameGenerator
from ...llm.base import BaseLLM
from ...player.agent.player import BaseAgentPlayer
from ..base import BaseConfigGym
from .common import TrainingConfig


class BaseAgentGym[MT, UT, CT, IT, HT, GT: BaseModel, FT, RT, ET: BaseModel](
    BaseConfigGym[
        CT,
        IT,
        HT,
        GT,
        FT,
        RT,
        [BaseLLM, bool, TrainingConfig | None, Callable[[str], None], Callable[[str], None]],
    ],
    ABC,
):
    def __init__(
        self,
        *,
        log_func: Callable[[str], None],
        game_generator: BaseGameGenerator[MT, UT, CT, BaseGame[IT, HT, GT, FT, RT]],
        **kwargs,
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)

        self._game_generator: BaseGameGenerator[MT, UT, CT, BaseGame[IT, HT, GT, FT, RT]] = (
            game_generator
        )

    @override
    def create_player_with_cb(
        self,
        model: BaseLLM,
        do_analyze: bool,
        training_config: TrainingConfig | None,
        player_log_func: Callable[[str], None],
        agent_log_func: Callable[[str], None],
    ) -> tuple[
        BaseAgentPlayer[IT, HT, GT, FT, ET],
        Callable[[], None],
        Callable[[GameRecord[IT, HT, GT, FT, RT]], None],
    ]:
        player: BaseAgentPlayer[IT, HT, GT, FT, ET] = self.create_player(
            model=model,
            do_analyze=do_analyze,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

        def prepare_player() -> None:
            if training_config is not None:
                for _ in range(training_config.num_train_loops):
                    for i in range(training_config.num_in_loop_trials):
                        player.memory.reflect(
                            game_record=self._game_generator.random_game().play(player=player),
                            update_experience=i == training_config.num_in_loop_trials - 1,
                        )

        def summarize_player(game_record: GameRecord[IT, HT, GT, FT, RT]) -> None:
            player.memory.reflect(game_record=game_record, update_experience=False)

        return player, prepare_player, summarize_player

    @override
    def create_game_from_config(self, *, config: CT) -> BaseGame[IT, HT, GT, FT, RT]:
        return self._game_generator.create_game_from_config(config=config)

    @abstractmethod
    def create_player(
        self,
        *,
        model: BaseLLM,
        do_analyze: bool,
        player_log_func: Callable[[str], None],
        agent_log_func: Callable[[str], None],
    ) -> BaseAgentPlayer[IT, HT, GT, FT, ET]:
        raise NotImplementedError()

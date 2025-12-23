from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override

from ..formatter.base import BaseFinalResultFormatter
from ..game.base import BaseGame
from ..game.common import GameRecord
from ..player.base import BasePlayer


class BaseGym[IT, HT, GT, FT, RT, **P](BaseFinalResultFormatter[RT], ABC):
    def __init__(self, *, log_func: Callable[[str], None], **kwargs) -> None:
        super().__init__(**kwargs)
        self._log_func: Callable[[str], None] = log_func

    def play(self, *player_args: P.args, **player_kwargs: P.kwargs) -> None:
        player: BasePlayer[IT, HT, GT, FT]
        prepare_player: Callable[[], None] | None
        summarize_player: Callable[[GameRecord[IT, HT, GT, FT, RT]], None] | None

        player, prepare_player, summarize_player = self.create_player_with_cb(
            *player_args, **player_kwargs
        )

        if prepare_player is not None:
            prepare_player()

        game_record: GameRecord = self.create_game().play(player=player)
        self._log_func(f"You Guessed {len(game_record.trajectory)} Times")

        for section in self.format_final_result(final_result=game_record.final_result):
            self._log_func(section)
        if summarize_player is not None:
            summarize_player(game_record)

    @abstractmethod
    def create_player_with_cb(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> tuple[
        BasePlayer[IT, HT, GT, FT],
        Callable[[], None] | None,
        Callable[[GameRecord[IT, HT, GT, FT, RT]], None] | None,
    ]:
        raise NotImplementedError()

    @abstractmethod
    def create_game(self) -> BaseGame[IT, HT, GT, FT, RT]:
        raise NotImplementedError()


class BaseConfigGym[CT, IT, HT, GT, FT, RT, **P](BaseGym[IT, HT, GT, FT, RT, P], ABC):
    def __init__(
        self, *, create_config_func: Callable[[], CT], log_func: Callable[[str], None], **kwargs
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._create_config_func: Callable[[], CT] = create_config_func

    @override
    def create_game(self) -> BaseGame[IT, HT, GT, FT, RT]:
        return self.create_game_from_config(config=self._create_config_func())

    @abstractmethod
    def create_game_from_config(self, *, config: CT) -> BaseGame[IT, HT, GT, FT, RT]:
        raise NotImplementedError()

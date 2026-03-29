from random import Random
from typing import override

from pydantic import TypeAdapter

from ....common.game.engine.base import BaseGameEngine
from ....common.game.state import GameStateInterface
from ....utils import create_seed, get_db_cursor
from ..common import (
    ConnectionsConfig,
    ConnectionsFeedback,
    ConnectionsFinalResult,
    ConnectionsGuess,
    ConnectionsInfo,
    ConnectionsWordGroup,
)


class ConnectionsGameEngine(
    BaseGameEngine[
        ConnectionsConfig,
        ConnectionsInfo,
        ConnectionsGuess,
        ConnectionsFeedback,
        ConnectionsFinalResult,
    ]
):
    def __init__(self, *, config: ConnectionsConfig) -> None:
        with get_db_cursor(data_file=config.data_file) as cur:
            groups: dict[str, list[str]] = TypeAdapter(dict[str, list[str]]).validate_json(
                cur.execute(
                    "SELECT groups FROM game WHERE game_id = ?", (config.game_id,)
                ).fetchone()[0],
                strict=True,
            )

        self._num_groups: int = len(groups)
        self._group_size: int = len(list(groups.values())[0])

        for indices in groups.values():
            assert len(indices) == self._group_size

        self._words: list[str] = sum(groups.values(), [])
        Random(create_seed(data="/".join(self._words))).shuffle(self._words)

        self._groups: dict[str, set[int]] = {
            theme: set(map(self._words.index, group)) for theme, group in groups.items()
        }

        self._max_turns: int = config.max_turns

    @override
    def start_game(self) -> ConnectionsInfo:
        self._found_themes: set[str] = set()
        self._remaining_indices: set[int] = set(range(len(self._words)))

        return ConnectionsInfo(
            words=self._words, group_size=self._group_size, max_turns=self._max_turns
        )

    @override
    def is_over(
        self,
        *,
        state: GameStateInterface[
            ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback, ConnectionsFinalResult
        ],
    ) -> bool:
        num_remains: int = self._num_groups - len(self._found_themes)
        return num_remains == 0 or len(state.turns) + num_remains > self._max_turns > 0

    @override
    def process_guess(self, *, guess: ConnectionsGuess) -> ConnectionsFeedback:
        indices: set[int] = set(guess.indices)

        if not (len(indices) == self._group_size and indices.issubset(self._remaining_indices)):
            return ConnectionsFeedback(accepted=False, message=None)

        for theme, theme_indices in self._groups.items():
            if theme_indices == indices:
                self._found_themes.add(theme)
                self._remaining_indices -= indices
                return ConnectionsFeedback(accepted=True, message=theme)

        return ConnectionsFeedback(accepted=True, message=None)

    @override
    def get_final_result(self) -> ConnectionsFinalResult:
        found_groups: list[ConnectionsWordGroup] = []
        remaining_groups: list[ConnectionsWordGroup] = []

        for theme, indices in self._groups.items():
            (found_groups if theme in self._found_themes else remaining_groups).append(
                ConnectionsWordGroup(theme=theme, words=[self._words[index] for index in indices])
            )

        return ConnectionsFinalResult(found_groups=found_groups, remaining_groups=remaining_groups)

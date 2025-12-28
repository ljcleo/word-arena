from collections.abc import Iterable, Mapping, Sequence
from typing import override

from ...common.game.base import BaseGame
from .common import (
    ConnectionsFeedback,
    ConnectionsFinalResult,
    ConnectionsGuess,
    ConnectionsInfo,
    ConnectionsWordGroup,
)


class ConnectionsGame(
    BaseGame[ConnectionsInfo, None, ConnectionsGuess, ConnectionsFeedback, ConnectionsFinalResult]
):
    def __init__(
        self, *, words: Sequence[str], groups: Mapping[str, Iterable[int]], max_guesses: int
    ) -> None:
        self._words: list[str] = list(words)

        self._groups: dict[str, set[int]] = {
            theme: set(indices) for theme, indices in groups.items()
        }

        self._max_guesses: int = max_guesses

        self._num_groups: int = len(self._groups)
        self._group_size: int = len(list(self._groups.values())[0])

        for indices in self._groups.values():
            assert len(indices) == self._group_size

    @override
    def start_game(self) -> ConnectionsInfo:
        self._found_themes: set[str] = set()
        self._remaining_indices: set[int] = set(range(len(self._words)))
        self._num_guesses: int = 0

        return ConnectionsInfo(
            words=self._words, group_size=self._group_size, max_guesses=self._max_guesses
        )

    @override
    def is_over(self) -> bool:
        num_remains: int = self._num_groups - len(self._found_themes)
        return num_remains == 0 or self._num_guesses + num_remains > self._max_guesses > 0

    @override
    def get_guess_prompt(self) -> None:
        pass

    @override
    def process_guess(self, *, guess: ConnectionsGuess) -> ConnectionsFeedback:
        self._num_guesses += 1
        indices: set[int] = set(guess.indices)

        if not (len(indices) == self._group_size and indices.issubset(self._remaining_indices)):
            return ConnectionsFeedback(accepted=False, message="Invalid guess")

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

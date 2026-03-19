from collections.abc import Iterable, Mapping, Sequence
from typing import override

from ....common.game.engine.base import BaseGameEngine
from ..common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo, ConexoWordGroup
from .common import ConexoGameStateInterface


class ConexoGameEngine(BaseGameEngine[ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult]):
    def __init__(
        self, *, words: Sequence[str], groups: Mapping[str, Iterable[int]], max_turns: int
    ) -> None:
        self._words: list[str] = list(words)

        self._groups: dict[str, set[int]] = {
            theme: set(indices) for theme, indices in groups.items()
        }

        self._max_turns: int = max_turns

        self._num_groups: int = len(self._groups)
        self._group_size: int = len(list(self._groups.values())[0])

        for indices in self._groups.values():
            assert len(indices) == self._group_size

    @override
    def start_game(self) -> ConexoInfo:
        self._found_themes: set[str] = set()
        self._remaining_indices: set[int] = set(range(len(self._words)))
        return ConexoInfo(words=self._words, group_size=self._group_size, max_turns=self._max_turns)

    @override
    def is_over(self, *, state: ConexoGameStateInterface) -> bool:
        num_remains: int = self._num_groups - len(self._found_themes)
        return num_remains == 0 or len(state.turns) + num_remains > self._max_turns > 0

    @override
    def process_guess(self, *, guess: ConexoGuess):
        indices: set[int] = set(guess.indices)

        if not (len(indices) == self._group_size and indices.issubset(self._remaining_indices)):
            return ConexoFeedback(accepted=False, message="Invalid guess")

        for theme, theme_indices in self._groups.items():
            if theme_indices == indices:
                self._found_themes.add(theme)
                self._remaining_indices -= indices
                return ConexoFeedback(accepted=True, message=theme)

        return ConexoFeedback(accepted=True, message=None)

    @override
    def get_final_result(self) -> ConexoFinalResult:
        found_groups: list[ConexoWordGroup] = []
        remaining_groups: list[ConexoWordGroup] = []

        for theme, indices in self._groups.items():
            (found_groups if theme in self._found_themes else remaining_groups).append(
                ConexoWordGroup(theme=theme, words=[self._words[index] for index in indices])
            )

        return ConexoFinalResult(found_groups=found_groups, remaining_groups=remaining_groups)

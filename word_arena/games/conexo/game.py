from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from random import Random
from typing import override

from pydantic import BaseModel

from ...common.game.base import BaseGame
from .common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo, ConexoWordGroup


class ConexoGame(BaseGame[ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoFinalResult]):
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
    def start_game(self) -> ConexoInfo:
        self._found_themes: set[str] = set()
        self._remaining_indices: set[int] = set(range(len(self._words)))
        self._num_guesses: int = 0

        return ConexoInfo(
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
    def process_guess(self, *, guess: ConexoGuess) -> ConexoFeedback:
        self._num_guesses += 1
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


class ConexoGroupData(BaseModel):
    indices: list[int]
    theme: str


class ConexoGameData(BaseModel):
    id: int
    words: list[str]
    groups: list[ConexoGroupData]


class ConexoGameManager:
    def __init__(self, *, games_dir: Path, seed: int) -> None:
        self._games_dir: Path = games_dir
        self._num_games: int = sum(1 for _ in games_dir.iterdir())
        self._rng: Random = Random(seed)

    def create_game(self, *, game_id: int, max_guesses: int) -> ConexoGame:
        with (self._games_dir / f"{game_id}.json").open("rb") as f:
            game_data: ConexoGameData = ConexoGameData.model_validate_json(f.read())

        return ConexoGame(
            words=game_data.words,
            groups={group.theme: group.indices for group in game_data.groups},
            max_guesses=max_guesses,
        )

    def create_random_game(self, *, param_candidates: Sequence[int]) -> ConexoGame:
        game_id: int = self._rng.randrange(self._num_games)
        max_guesses: int = self._rng.choice(param_candidates)
        return self.create_game(game_id=game_id, max_guesses=max_guesses)

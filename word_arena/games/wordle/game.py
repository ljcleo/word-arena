from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from random import Random
from typing import override

from ...common.game.base import BaseGame
from .common import (
    WordleError,
    WordleFeedback,
    WordleFinalResult,
    WordleInfo,
    WordleResponse,
    WordleGuess,
)


class WordleGame(BaseGame[WordleInfo, None, WordleGuess, WordleFeedback, WordleFinalResult]):
    def __init__(
        self, *, word_list: Sequence[str], target_ids: list[int], max_guesses: int
    ) -> None:
        self._word_list: set[str] = set(word_list)
        self._answers: list[str] = [word_list[target_id] for target_id in target_ids]
        self._max_guesses: int = max_guesses

        self._num_targets: int = len(self._answers)
        self._num_letters: int = len(self._answers[0])

        for answer in self._answers:
            assert len(answer) == self._num_letters

    @override
    def start_game(self) -> WordleInfo:
        self._found_indices: set[int] = set()
        self._num_guesses: int = 0
        return WordleInfo(num_targets=self._num_targets, max_guesses=self._max_guesses)

    @override
    def is_over(self) -> bool:
        num_remains: int = self._num_targets - len(self._found_indices)
        return num_remains == 0 or self._num_guesses + num_remains > self._max_guesses > 0

    @override
    def get_guess_prompt(self) -> None:
        pass

    @override
    def process_guess(self, *, guess: WordleGuess) -> WordleFeedback:
        self._num_guesses += 1
        word: str = guess.word

        if not (len(word) == self._num_letters and word.isalpha() and word.islower()):
            return WordleError(error="Invalid guess")
        elif word not in self._word_list:
            return WordleError(error="Unknown word")

        patterns: list[str] = []

        for index, answer in enumerate(self._answers):
            if word == answer:
                self._found_indices.add(index)

            buffer: list[str] = ["." for _ in answer]
            counter: Counter = Counter(answer)

            for i, (x, y) in enumerate(zip(word, answer)):
                if x == y:
                    buffer[i] = "G"
                    counter[y] -= 1

            for i, x in enumerate(word):
                if buffer[i] != "G" and counter[x] > 0:
                    buffer[i] = "Y"
                    counter[x] -= 1

            patterns.append("".join(buffer))

        return WordleResponse(patterns=patterns)

    @override
    def get_final_result(self) -> WordleFinalResult:
        return WordleFinalResult(found_indices=self._found_indices, answers=self._answers)


class WordleGameManager:
    def __init__(self, *, word_list_file: Path, seed: int) -> None:
        with word_list_file.open(encoding="utf8") as f:
            self._word_list: list[str] = list(map(str.strip, f))

        self._num_games: int = len(self._word_list)
        self._rng: Random = Random(seed)

    def create_game(self, *, target_ids: list[int], max_guesses: int) -> WordleGame:
        return WordleGame(word_list=self._word_list, target_ids=target_ids, max_guesses=max_guesses)

    def create_random_game(self, *, param_candidates: Sequence[tuple[int, int]]) -> WordleGame:
        num_targets: int
        max_guesses: int
        num_targets, max_guesses = self._rng.choice(param_candidates)
        target_ids = self._rng.sample(range(self._num_games), num_targets)
        return self.create_game(target_ids=target_ids, max_guesses=max_guesses)

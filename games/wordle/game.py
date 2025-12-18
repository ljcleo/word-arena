from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from random import Random
from typing import override

from common.game import BaseGame
from games.wordle.common import WordleError, WordleInfo, WordleResponse, WordleResult


class WordleGame(BaseGame[WordleInfo, None, str, WordleResult, list[str]]):
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
        self._solved_targets: set[int] = set()
        self._num_guesses: int = 0
        return WordleInfo(num_targets=self._num_targets, max_guesses=self._max_guesses)

    @override
    def is_over(self) -> bool:
        num_remains: int = self._num_targets - len(self._solved_targets)
        return num_remains == 0 or self._num_guesses + num_remains > self._max_guesses > 0

    @override
    def get_guess_prompt(self) -> None:
        pass

    @override
    def process_guess(self, *, guess: str) -> WordleResult:
        self._num_guesses += 1

        if not (len(guess) == self._num_letters and guess.isalpha() and guess.islower()):
            return WordleError(error="Invalid guess")
        elif guess not in self._word_list:
            return WordleError(error="Unknown word")

        results: list[str] = []

        for idx, answer in enumerate(self._answers):
            if guess == answer:
                self._solved_targets.add(idx)

            buffer: list[str] = ["." for _ in answer]
            counter: Counter = Counter(answer)

            for i, (x, y) in enumerate(zip(guess, answer)):
                if x == y:
                    buffer[i] = "G"
                    counter[y] -= 1

            for i, x in enumerate(guess):
                if buffer[i] != "G" and counter[x] > 0:
                    buffer[i] = "Y"
                    counter[x] -= 1

            results.append("".join(buffer))

        return WordleResponse(results=results)

    @override
    def get_final_result(self) -> list[str]:
        return self._answers


class WordleGameManager:
    def __init__(self, *, word_list_file: Path, seed: int) -> None:
        with word_list_file.open(encoding="utf8") as f:
            self._word_list: list[str] = list(map(str.strip, f))

        self._num_games: int = len(self._word_list)
        self._rng: Random = Random(seed)

    def create_game(self, *, target_ids: list[int], max_guesses: int) -> WordleGame:
        return WordleGame(word_list=self._word_list, target_ids=target_ids, max_guesses=max_guesses)

    def create_random_game(self, *, param_candidates: list[tuple[int, int]]) -> WordleGame:
        num_targets: int
        max_guesses: int
        num_targets, max_guesses = self._rng.choice(param_candidates)
        target_ids = self._rng.sample(range(self._num_games), num_targets)
        print("Current Word IDs:", *target_ids)
        print("Current Max Guesses:", max_guesses)
        return self.create_game(target_ids=target_ids, max_guesses=max_guesses)

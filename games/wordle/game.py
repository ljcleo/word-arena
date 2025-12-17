from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from random import Random
from typing import override

from common.game import BaseGame
from games.wordle.common import WordleError, WordleInfo, WordleResponse, WordleResult


class WordleGame(BaseGame[WordleInfo, None, str, WordleResult, list[str]]):
    def __init__(
        self, *, word_list: Sequence[str], target_ids: list[int], max_accept_guesses: int
    ) -> None:
        self._word_list: set[str] = set(word_list)
        self._answers: list[str] = [word_list[target_id] for target_id in target_ids]
        self._max_accept_guesses: int = max_accept_guesses

    @override
    def start_game(self) -> WordleInfo:
        self._num_accept_guesses: int = 0
        self._solved_targets: set[int] = set()

        return WordleInfo(
            num_targets=len(self._answers), max_accept_guesses=self._max_accept_guesses
        )

    @override
    def is_over(self) -> bool:
        return (
            len(self._solved_targets) == len(self._answers)
            or self._num_accept_guesses >= self._max_accept_guesses
        )

    @override
    def get_guess_prompt(self) -> None:
        pass

    @override
    def process_guess(self, *, guess: str) -> WordleResult:
        if not (len(guess) == len(self._answers[0]) and guess.isalpha() and guess.islower()):
            return WordleError(error="Invalid guess")
        elif guess not in self._word_list:
            return WordleError(error="Unknown word")

        self._num_accept_guesses += 1
        results: list[str] = []

        for idx, answer in enumerate(self._answers):
            if guess == answer:
                self._solved_targets.add(idx)

            buffer: list[str] = ["-"] * len(answer)
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
    def summarize_game(self) -> list[str]:
        return self._answers


class WordleGameManager:
    def __init__(self, *, word_list_file: Path, seed: int) -> None:
        with word_list_file.open(encoding="utf8") as f:
            self._word_list: list[str] = list(map(str.strip, f))

        self._num_games: int = len(self._word_list)
        self._rng: Random = Random(seed)

    def create_game(self, *, target_ids: list[int], max_accept_guesses: int) -> WordleGame:
        return WordleGame(
            word_list=self._word_list, target_ids=target_ids, max_accept_guesses=max_accept_guesses
        )

    def create_random_game(self, *, param_candidates: list[tuple[int, int]]) -> WordleGame:
        num_targets: int
        max_accept_guesses: int
        num_targets, max_accept_guesses = self._rng.choice(param_candidates)

        return self.create_game(
            target_ids=self._rng.sample(range(self._num_games), num_targets),
            max_accept_guesses=max_accept_guesses,
        )

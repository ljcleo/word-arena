from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from random import Random
from typing import override

from common.game import BaseGame
from games.letroso.common import LetrosoError, LetrosoInfo, LetrosoResponse, LetrosoResult


class LetrosoGame(BaseGame[LetrosoInfo, None, str, LetrosoResult, list[str]]):
    def __init__(
        self, *, word_list: Sequence[str], target_ids: list[int], max_letters: int, max_guesses: int
    ) -> None:
        self._word_list: set[str] = set(word_list)
        self._answers: list[str] = [word_list[target_id] for target_id in target_ids]
        self._max_letters: int = max_letters
        self._max_guesses: int = max_guesses

        self._num_targets: int = len(self._answers)

    @override
    def start_game(self) -> LetrosoInfo:
        self._solved_targets: set[int] = set()
        self._num_guesses: int = 0

        return LetrosoInfo(
            num_targets=self._num_targets,
            max_letters=self._max_letters,
            max_guesses=self._max_guesses,
        )

    @override
    def is_over(self) -> bool:
        return (
            len(self._solved_targets) == self._num_targets
            or self._num_guesses >= self._max_guesses > 0
        )

    @override
    def get_guess_prompt(self) -> None:
        pass

    @override
    def process_guess(self, *, guess: str) -> LetrosoResult:
        self._num_guesses += 1

        if not (1 <= len(guess) <= self._max_letters and guess.isalpha() and guess.islower()):
            return LetrosoError(error="Invalid guess")
        elif guess not in self._word_list:
            return LetrosoError(error="Unknown word")

        results: list[str] = []

        for idx, answer in enumerate(self._answers):
            if guess == answer:
                self._solved_targets.add(idx)

            buffer: list[str] = []
            head_match: bool = False
            tail_match: bool = False
            past_counter: Counter = Counter()
            next_counter: Counter = Counter(answer)
            pivot: int = 0

            for i, c in enumerate(guess):
                if next_counter[c] > 0:
                    if answer[pivot] == c and len(buffer) > 0 and buffer[-1][-1] == "G":
                        buffer[-1] = f"{buffer[-1]}G"
                    else:
                        buffer.append("G")

                    while answer[pivot] != c:
                        past_counter[answer[pivot]] += 1
                        next_counter[answer[pivot]] -= 1
                        pivot += 1

                    if i == 0 and pivot == 0:
                        head_match = True
                    if i == len(guess) - 1 and pivot == len(answer) - 1:
                        tail_match = True

                    next_counter[answer[pivot]] -= 1
                    pivot += 1
                elif past_counter[c] > 0:
                    buffer.append("Y")
                    past_counter[c] -= 1
                else:
                    buffer.append(".")

            results.append(
                "".join(
                    f"{'(' if head_match and i == 0 else '['}{s}"
                    f"{')' if tail_match and i == len(buffer) - 1 else ']'}"
                    for i, s in enumerate(buffer)
                )
            )

        return LetrosoResponse(results=results)

    @override
    def summarize_game(self) -> list[str]:
        return self._answers


class LetrosoGameManager:
    def __init__(self, *, word_list_file: Path, seed: int) -> None:
        with word_list_file.open(encoding="utf8") as f:
            self._word_list: list[str] = list(map(str.strip, f))

        self._num_games: int = len(self._word_list)
        self._rng: Random = Random(seed)

    def create_game(
        self, *, target_ids: list[int], max_letters: int, max_guesses: int
    ) -> LetrosoGame:
        return LetrosoGame(
            word_list=self._word_list,
            target_ids=target_ids,
            max_letters=max_letters,
            max_guesses=max_guesses,
        )

    def create_random_game(self, *, param_candidates: list[tuple[int, int, int]]) -> LetrosoGame:
        num_targets: int
        max_letters: int
        max_guesses: int
        num_targets, max_letters, max_guesses = self._rng.choice(param_candidates)
        target_ids = self._rng.sample(range(self._num_games), num_targets)
        print("Current Word IDs:", *target_ids)
        print("Current Max Letters:", max_letters)
        print("Current Max Guesses:", max_guesses)

        return self.create_game(
            target_ids=target_ids, max_letters=max_letters, max_guesses=max_guesses
        )

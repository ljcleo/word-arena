from collections import Counter
from collections.abc import Iterable, Sequence
from typing import override

from ...common.game.base import BaseGame
from .common import (
    LetrosoError,
    LetrosoFeedback,
    LetrosoFinalResult,
    LetrosoGuess,
    LetrosoInfo,
    LetrosoResponse,
)


class LetrosoGame(BaseGame[LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult]):
    def __init__(
        self,
        *,
        word_list: Sequence[str],
        target_ids: Iterable[int],
        max_letters: int,
        max_guesses: int,
    ) -> None:
        self._word_list: set[str] = set(word_list)
        self._answers: list[str] = [word_list[target_id] for target_id in target_ids]
        self._max_letters: int = max_letters
        self._max_guesses: int = max_guesses

        self._num_targets: int = len(self._answers)

    @override
    def start_game(self) -> LetrosoInfo:
        self._found_indices: set[int] = set()
        self._num_guesses: int = 0

        return LetrosoInfo(
            num_targets=self._num_targets,
            max_letters=self._max_letters,
            max_guesses=self._max_guesses,
        )

    @override
    def is_over(self) -> bool:
        num_remains: int = self._num_targets - len(self._found_indices)
        return num_remains == 0 or self._num_guesses + num_remains > self._max_guesses > 0

    @override
    def get_guess_prompt(self) -> None:
        pass

    @override
    def process_guess(self, *, guess: LetrosoGuess) -> LetrosoFeedback:
        self._num_guesses += 1
        word: str = guess.word

        if not (1 <= len(word) <= self._max_letters and word.isalpha() and word.islower()):
            return LetrosoError(error="Invalid guess")
        elif word not in self._word_list:
            return LetrosoError(error="Unknown word")

        patterns: list[str] = []

        for index, answer in enumerate(self._answers):
            if word == answer:
                self._found_indices.add(index)

            buffer: list[str] = []
            head_match: bool = False
            tail_match: bool = False
            past_counter: Counter = Counter()
            next_counter: Counter = Counter(answer)
            pivot: int = 0

            for i, c in enumerate(word):
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
                    if i == len(word) - 1 and pivot == len(answer) - 1:
                        tail_match = True

                    next_counter[answer[pivot]] -= 1
                    pivot += 1
                elif past_counter[c] > 0:
                    buffer.append("Y")
                    past_counter[c] -= 1
                else:
                    buffer.append(".")

            patterns.append(
                "".join(
                    f"{'(' if head_match and i == 0 else '['}{s}"
                    f"{')' if tail_match and i == len(buffer) - 1 else ']'}"
                    for i, s in enumerate(buffer)
                )
            )

        return LetrosoResponse(patterns=patterns)

    @override
    def get_final_result(self) -> LetrosoFinalResult:
        return LetrosoFinalResult(found_indices=self._found_indices, answers=self._answers)

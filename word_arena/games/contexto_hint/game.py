from collections.abc import Iterable
from random import Random
from typing import override

from ...common.game.base import BaseGame
from .common import ContextoHintGuess


class ContextoHintGame(BaseGame[None, list[str], ContextoHintGuess, int, list[str]]):
    def __init__(self, *, top_words: Iterable[str], num_candidates: int) -> None:
        self._top_words: list[str] = list(top_words)
        self._num_candidates: int = num_candidates

    @override
    def start_game(self) -> None:
        self._used_pos: set[int] = set()
        self._best_pos: int = len(self._top_words)
        self._last_pos: int = self._best_pos

    @override
    def is_over(self) -> bool:
        return self._best_pos == 0

    @override
    def get_guess_prompt(self) -> list[str]:
        rng: Random = Random(self._last_pos)
        half: int = (self._best_pos >> 1) + 1
        head_start: int = max(half - self._num_candidates, 0)
        head_stop: int = min(half + self._num_candidates + 1, self._best_pos)

        tail: list[int] = [
            x for x in range(head_stop, len(self._top_words)) if x not in self._used_pos
        ]

        num_tail_sample: int = self._num_candidates - 1

        if len(tail) < num_tail_sample:
            head_start = 0
            head_stop = 1
            tail = [*range(1, head_stop), *tail]

            if len(tail) < num_tail_sample:
                tail.extend(tail[-1] for _ in range(num_tail_sample - len(tail)))

        self._candidate_pos: list[int] = [
            rng.randrange(head_start, head_stop),
            *rng.sample(tail, num_tail_sample),
        ]

        rng.shuffle(self._candidate_pos)
        return [self._top_words[pos] for pos in self._candidate_pos]

    @override
    def process_guess(self, *, guess: ContextoHintGuess) -> int:
        index: int = guess.index
        if not 0 <= index < self._num_candidates:
            return -1

        self._last_pos = self._candidate_pos[index]
        self._used_pos.add(self._last_pos)
        self._best_pos = min(self._best_pos, self._last_pos)
        return self._last_pos

    @override
    def get_final_result(self) -> list[str]:
        return self._top_words

from random import Random
from typing import override

from pydantic import TypeAdapter

from ....common.game.engine.base import BaseGameEngine
from ....utils import get_db_cursor
from ..common import ContextoHintConfig, ContextoHintFeedback, ContextoHintGuess
from .state import ContextoHintGameStateInterface


class ContextoHintGameEngine(
    BaseGameEngine[
        ContextoHintConfig, list[str], ContextoHintGuess, ContextoHintFeedback, list[str]
    ]
):
    def __init__(self, *, config: ContextoHintConfig) -> None:
        with get_db_cursor(data_file=config.data_file) as cur:
            self._top_words: list[str] = TypeAdapter(list[str]).validate_json(
                cur.execute(
                    "SELECT top_words FROM game WHERE game_id = ?", (config.game_id,)
                ).fetchone()[0]
            )

        self._num_candidates: int = config.num_candidates

    @override
    def start_game(self) -> list[str]:
        self._used_pos: set[int] = set()
        self._best_pos: int = len(self._top_words)
        self._last_pos: int = self._best_pos
        return self._get_next_choices()

    @override
    def is_over(self, *, state: ContextoHintGameStateInterface) -> bool:
        return self._best_pos == 0

    @override
    def process_guess(self, *, guess: ContextoHintGuess) -> ContextoHintFeedback:
        index: int = guess.index
        distance: int = -1

        if 0 <= index < self._num_candidates:
            self._last_pos = self._candidate_pos[index]
            self._used_pos.add(self._last_pos)
            self._best_pos = min(self._best_pos, self._last_pos)
            distance = self._last_pos

        return ContextoHintFeedback(
            distance=distance, next_choices=None if distance == 0 else self._get_next_choices()
        )

    @override
    def get_final_result(self) -> list[str]:
        return self._top_words

    def _get_next_choices(self) -> list[str]:
        assert self._last_pos != 0
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

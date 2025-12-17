from pathlib import Path
from random import Random
from typing import override

from common.game import BaseGame


class ContextoHintGame(BaseGame[int, list[str], int, int, list[str]]):
    def __init__(self, *, top_words: list[str], num_candidates: int, rng: Random) -> None:
        self._top_words: list[str] = top_words
        self._num_candidates: int = num_candidates
        self._rng: Random = rng

    @override
    def start_game(self) -> int:
        self._used_pos: set[int] = set()
        self._best_pos: int = len(self._top_words)
        return self._num_candidates

    @override
    def is_over(self) -> bool:
        return self._best_pos == 0

    @override
    def get_guess_prompt(self) -> list[str]:
        half: int = (self._best_pos >> 1) + 1
        head: list[int] = list(range(max(half - self._num_candidates, 0), half))
        tail: list[int] = [x for x in range(half, len(self._top_words)) if x not in self._used_pos]
        num_tail_sample: int = self._num_candidates - 1

        if len(tail) < num_tail_sample:
            head = [0]
            tail = list(range(1, half)) + tail

            if len(tail) < num_tail_sample:
                tail.extend(tail[-1] for _ in range(num_tail_sample - len(tail)))

        self._candidate_pos: list[int] = [
            self._rng.choice(head),
            *self._rng.sample(tail, num_tail_sample),
        ]

        self._rng.shuffle(self._candidate_pos)
        return [self._top_words[pos] for pos in self._candidate_pos]

    @override
    def process_guess(self, *, guess: int) -> int:
        pos: int = self._candidate_pos[guess]
        self._used_pos.add(pos)
        self._best_pos = min(self._best_pos, pos)
        return pos

    @override
    def summarize_game(self) -> list[str]:
        return self._top_words


class ContextoHintGameManager:
    def __init__(self, *, games_dir: Path, seed: int) -> None:
        self._games_dir: Path = games_dir
        self._num_games: int = sum(1 for _ in games_dir.iterdir())
        self._rng: Random = Random(seed)

    def create_game(self, *, game_id: int | None, num_candidates: int) -> ContextoHintGame:
        if game_id is None:
            game_id = self._rng.randrange(self._num_games)
            print("Current Game ID:", game_id)

        return ContextoHintGame(
            top_words=(self._games_dir / f"{game_id}.txt").read_text().strip().split(),
            num_candidates=num_candidates,
            rng=self._rng,
        )

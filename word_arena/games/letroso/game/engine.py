from collections import Counter
from typing import override

from ....common.game.engine.base import BaseGameEngine
from ....common.game.state import GameStateInterface
from ..common import (
    LetrosoConfig,
    LetrosoFeedback,
    LetrosoFinalResult,
    LetrosoGuess,
    LetrosoInfo,
)


class LetrosoGameEngine(
    BaseGameEngine[LetrosoConfig, LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult]
):
    def __init__(self, *, config: LetrosoConfig) -> None:
        self._word_bank: set[str] = set(config.word_pool.values())
        self._answers: list[str] = [config.word_pool[target_id] for target_id in config.game_ids]
        self._max_letters: int = config.max_letters
        self._max_turns: int = config.max_turns
        self._num_targets: int = len(self._answers)

    @override
    def start_game(self) -> LetrosoInfo:
        self._found_indices: set[int] = set()

        return LetrosoInfo(
            num_targets=self._num_targets,
            max_letters=self._max_letters,
            max_turns=self._max_turns,
        )

    @override
    def is_over(
        self,
        *,
        state: GameStateInterface[LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult],
    ) -> bool:
        num_remains: int = self._num_targets - len(self._found_indices)
        return num_remains == 0 or len(state.turns) + num_remains > self._max_turns > 0

    @override
    def process_guess(self, *, guess: LetrosoGuess) -> LetrosoFeedback:
        word: str = guess.word

        if not (1 <= len(word) <= self._max_letters and word.isalpha() and word.islower()):
            return False
        elif word not in self._word_bank:
            return True

        patterns: list[str] = []

        for index, answer in enumerate(self._answers):
            patterns.append(self._calc_pattern(answer=answer, guess=word))
            if word == answer:
                self._found_indices.add(index)

        return patterns

    @override
    def get_final_result(self) -> LetrosoFinalResult:
        return LetrosoFinalResult(found_indices=self._found_indices, answers=self._answers)

    def _calc_pattern(self, *, answer: str, guess: str) -> str:
        answer_len: int = len(answer)
        guess_len: int = len(guess)

        edit_dist: dict[tuple[int, int], tuple[int, list[str]]] = {
            (i, j): (i + j + (i > 0 and j > 0), [])
            for i in range(answer_len + 1)
            for j in range(guess_len + 1)
        }

        for i in range(0, answer_len + 1):
            edit_dist[i, 0][1].append("+" * i)
        for j in range(1, guess_len + 1):
            edit_dist[0, j][1].append("-" * j)

        for i in range(1, answer_len + 1):
            for j in range(1, guess_len + 1):
                can_skip: bool = answer[i - 1] == guess[j - 1]
                skip_cost: int = edit_dist[i - can_skip, j - can_skip][0]
                add_cost: int = edit_dist[i - 1, j][0] + 1
                del_cost: int = edit_dist[i, j - 1][0] + 1
                min_cost: int = min(skip_cost, add_cost, del_cost)

                if skip_cost == min_cost:
                    edit_dist[i, j][1].extend(f"{path}>" for path in edit_dist[i - 1, j - 1][1])
                if add_cost == min_cost:
                    edit_dist[i, j][1].extend(f"{path}+" for path in edit_dist[i - 1, j][1])
                if del_cost == min_cost:
                    edit_dist[i, j][1].extend(f"{path}-" for path in edit_dist[i, j - 1][1])

                edit_dist[i, j] = min_cost, edit_dist[i, j][1]

        best_score: int = -1
        best_pattern: tuple[str, bool, bool] | None = None

        for path in edit_dist[answer_len, guess_len][1]:
            head_match: bool = path[0] == ">"
            tail_match: bool = path[-1] == ">"
            letter_pool: Counter[str] = Counter(answer)
            pattern_buffer: list[str] = []
            match_seg_len: int = 0
            score: int = head_match + tail_match

            for step in path:
                if step == ">":
                    letter_pool[guess[len(pattern_buffer)]] -= 1
                    pattern_buffer.append("G" if match_seg_len == 0 else ">")
                    match_seg_len += 1
                    score += match_seg_len * 3
                else:
                    match_seg_len = 0

                    if step == "-":
                        pattern_buffer.append(".")

            for pos, letter in enumerate(guess):
                if pattern_buffer[pos] == "." and letter_pool[letter] > 0:
                    letter_pool[letter] -= 1
                    pattern_buffer[pos] = "Y"

            pattern: tuple[str, bool, bool] = "".join(pattern_buffer), head_match, tail_match

            if score > best_score:
                best_score = score
                best_pattern = pattern
            elif score == best_score and (best_pattern is None or pattern[0] < best_pattern[0]):
                best_pattern = pattern

        assert best_pattern is not None

        return "".join(
            ("(" if best_pattern[1] else "[", best_pattern[0], ")" if best_pattern[2] else "]")
        )

from collections import Counter
from typing import override

from ....common.game.engine.base import BaseGameEngine
from ....common.game.state import GameStateInterface
from ..common import WordleConfig, WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo


class WordleGameEngine(
    BaseGameEngine[WordleConfig, WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult]
):
    def __init__(self, *, config: WordleConfig) -> None:
        self._word_bank: set[str] = set(config.word_pool.values())
        self._answers: list[str] = [config.word_pool[target_id] for target_id in config.game_ids]
        self._max_turns: int = config.max_turns
        self._num_targets: int = len(self._answers)
        self._num_letters: int = len(self._answers[0])

        for answer in self._answers:
            assert len(answer) == self._num_letters

    @override
    def start_game(self) -> WordleInfo:
        self._found_indices: set[int] = set()
        return WordleInfo(num_targets=self._num_targets, max_turns=self._max_turns)

    @override
    def is_over(
        self,
        *,
        state: GameStateInterface[WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult],
    ) -> bool:
        num_remains: int = self._num_targets - len(self._found_indices)
        return num_remains == 0 or len(state.turns) + num_remains > self._max_turns > 0

    @override
    def process_guess(self, *, guess: WordleGuess) -> WordleFeedback:
        word: str = guess.word

        if not (len(word) == self._num_letters and word.isalpha() and word.islower()):
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
    def get_final_result(self) -> WordleFinalResult:
        return WordleFinalResult(found_indices=self._found_indices, answers=self._answers)

    def _calc_pattern(self, *, answer: str, guess: str) -> str:
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

        return "".join(buffer)

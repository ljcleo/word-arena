from collections import Counter
from fractions import Fraction
from typing import override

from ....common.game.engine.base import BaseGameEngine
from ..common import (
    NumberleConfig,
    NumberleError,
    NumberleFeedback,
    NumberleFinalResult,
    NumberleGuess,
    NumberleInfo,
    NumberleResponse,
)
from .state import NumberleGameStateInterface


class NumberleGameEngine(
    BaseGameEngine[
        NumberleConfig, NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult
    ]
):
    def __init__(self, *, config: NumberleConfig) -> None:
        self._answers: list[str] = [config.eq_pool[target_id] for target_id in config.game_ids]
        self._eq_length: int = config.eq_length
        self._max_turns: int = config.max_turns
        self._num_targets: int = len(self._answers)

        for answer in self._answers:
            assert len(answer) == self._eq_length

    @override
    def start_game(self) -> NumberleInfo:
        self._found_indices: set[int] = set()

        return NumberleInfo(
            num_targets=self._num_targets, eq_length=self._eq_length, max_turns=self._max_turns
        )

    @override
    def is_over(self, *, state: NumberleGameStateInterface) -> bool:
        num_remains: int = self._num_targets - len(self._found_indices)
        return num_remains == 0 or len(state.turns) + num_remains > self._max_turns > 0

    @override
    def process_guess(self, *, guess: NumberleGuess) -> NumberleFeedback:
        eq: str = guess.equation

        if not (len(eq) == self._eq_length and self._validate_eq(eq=eq)):
            return NumberleError(error="Invalid guess")

        patterns: list[str] = []

        for index, answer in enumerate(self._answers):
            patterns.append(self._calc_pattern(answer=answer, guess=eq))
            if eq == answer:
                self._found_indices.add(index)

        return NumberleResponse(patterns=patterns)

    @override
    def get_final_result(self) -> NumberleFinalResult:
        return NumberleFinalResult(found_indices=self._found_indices, answers=self._answers)

    def _validate_eq(self, *, eq: str) -> bool:
        if eq.count("=") != 1:
            return False

        left_expr: str
        right_expr: str
        left_expr, _, right_expr = eq.partition("=")

        left_result: Fraction | None = self._calc_expr(expr=left_expr)
        if left_result is None:
            return False

        return left_result == self._calc_expr(expr=right_expr)

    def _calc_expr(self, *, expr: str) -> Fraction | None:
        try:
            components: list[str] = []

            for x in expr:
                if x.isdigit():
                    if len(components) > 0 and components[-1].isdigit():
                        if components[-1] == "0":
                            return None

                        components[-1] += x
                    else:
                        components.append(x)
                else:
                    if not (x in "+-*/" and len(components) > 0 and components[-1].isdigit()):
                        return None

                    components.append(x)

            if not (len(components) > 0 and components[-1].isdigit()):
                return None

            return eval("".join(f"Fraction({x})" if x.isdigit() else x for x in components))
        except Exception as e:
            print(e)
            return None

    def _calc_pattern(self, *, answer: str, guess: str) -> str:
        buffer: list[str] = ["." for _ in answer]
        counter: Counter = Counter(answer)

        for i, (x, y) in enumerate(zip(guess, answer)):
            if x == y:
                buffer[i] = "G"
                counter[y] -= 1

        for i, x in enumerate(guess):
            if buffer[i] == "." and counter[x] > 0:
                buffer[i] = "Y"
                counter[x] -= 1

        return "".join(buffer)

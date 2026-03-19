from collections.abc import Callable
from typing import override

from ....common.game.engine.base import BaseGameEngine
from ..common import TuringFeedback, TuringFinalResult, TuringGuess, TuringInfo
from .common import TuringGameStateInterface


class TuringGameEngine(BaseGameEngine[TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult]):
    def __init__(
        self, *, code: int, verifiers: list[list[str]], keys: list[int], max_turns: int
    ) -> None:
        self._answer: int = code
        self._verifiers: list[list[str]] = verifiers
        self._max_turns: int = max_turns

        self._criteria: list[Callable[[int, int, int], bool]] = [
            eval(f"lambda x, y, z: {verifier[key]}") for verifier, key in zip(verifiers, keys)
        ]

    @override
    def start_game(self) -> TuringInfo:
        self._num_questions: int = 0
        self._final_verdict: bool | None = None
        return TuringInfo(verifiers=self._verifiers, max_turns=self._max_turns)

    @override
    def is_over(self, *, state: TuringGameStateInterface) -> bool:
        return self._final_verdict is not None or len(state.turns) >= self._max_turns > 0

    @override
    def process_guess(self, *, guess: TuringGuess) -> TuringFeedback:
        code: int = guess.code
        verifiers: list[int] = guess.verifiers

        if code < 111 or code > 555:
            return "Invalid code guess"

        x: int = code // 100
        y: int = code // 10 % 10
        z: int = code % 10

        if x < 1 or x > 5 or y < 1 or y > 5 or z < 1 or z > 5:
            return "Invalid code guess"
        if len(verifiers) > 3:
            return "Too many verifiers"
        if any(i < 0 or i >= len(self._verifiers) for i in verifiers):
            return "Invalid verifier index"

        if len(verifiers) == 0:
            self._final_verdict = code == self._answer
            return self._final_verdict

        self._num_questions += len(verifiers)
        return [self._criteria[i](x, y, z) for i in verifiers]

    @override
    def get_final_result(self) -> TuringFinalResult:
        return TuringFinalResult(
            verdict=self._final_verdict, num_questions=self._num_questions, answer=self._answer
        )

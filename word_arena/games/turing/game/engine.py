from collections.abc import Callable
from typing import override

from ....common.game.engine.base import BaseGameEngine
from ....utils import get_db_cursor
from ..common import (
    TuringConfig,
    TuringError,
    TuringFeedback,
    TuringFinalResult,
    TuringGuess,
    TuringInfo,
)
from .state import TuringGameStateInterface


class TuringGameEngine(
    BaseGameEngine[TuringConfig, TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult]
):
    def __init__(self, *, config: TuringConfig) -> None:
        with get_db_cursor(data_file=config.data_file) as cur:
            card_id: int
            key: int
            self._answer: int

            card_id, key, self._answer = cur.execute(
                f"SELECT card_id, key, code FROM game_{config.num_verifiers} WHERE game_id = ?",
                (config.game_id,),
            ).fetchone()

        def unpack(*, data: int, base: int, n: int) -> list[int]:
            buf: list[int] = []

            for _ in range(n):
                buf.append(data % base)
                data //= base

            return buf[::-1]

        self._verifiers: list[list[str]] = [
            config.card_pool[i] for i in unpack(data=card_id, base=64, n=config.num_verifiers)
        ]

        self._criteria: list[Callable[[int, int, int], bool]] = [
            eval(f"lambda x, y, z: {verifier[key]}")
            for verifier, key in zip(
                self._verifiers, unpack(data=key, base=16, n=config.num_verifiers)
            )
        ]

        self._max_turns: int = config.max_turns

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
            return TuringError.INVALID_CODE

        x: int = code // 100
        y: int = code // 10 % 10
        z: int = code % 10

        if x < 1 or x > 5 or y < 1 or y > 5 or z < 1 or z > 5:
            return TuringError.INVALID_CODE
        if len(verifiers) > 3:
            return TuringError.TOO_MANY_VERIFIERS
        if any(i < 0 or i >= len(self._verifiers) for i in verifiers):
            return TuringError.INVALID_VERIFIER

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

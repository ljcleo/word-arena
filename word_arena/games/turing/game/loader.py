from typing import override

from ....common.game.loader.base import BaseGameLoader
from ....utils import get_db_cursor
from ..common import TuringFeedback, TuringFinalResult, TuringGuess, TuringInfo
from .common import TuringConfig
from .engine import TuringGameEngine


class TuringGameLoader(
    BaseGameLoader[TuringConfig, TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult]
):
    @override
    def create_engine(self, *, config: TuringConfig) -> TuringGameEngine:
        with get_db_cursor(data_file=config.data_file) as cur:
            card_id: int
            key: int
            code: int

            card_id, key, code = cur.execute(
                f"SELECT card_id, key, code FROM game_{config.num_verifiers} WHERE game_id = ?",
                (config.game_id,),
            ).fetchone()

        return TuringGameEngine(
            code=code,
            verifiers=[
                config.card_pool[i]
                for i in self._unpack(data=card_id, base=64, n=config.num_verifiers)
            ],
            keys=self._unpack(data=key, base=16, n=config.num_verifiers),
            max_turns=config.max_turns,
        )

    def _unpack(self, *, data: int, base: int, n: int) -> list[int]:
        buf: list[int] = []

        for _ in range(n):
            buf.append(data % base)
            data //= base

        return buf[::-1]

from typing import override

from ....common.generator.provider import BaseGameProvider
from ....common.utils import get_db_cursor
from ..game import TuringGame
from .common import TuringConfig, TuringMetaConfig


class TuringGameProvider(BaseGameProvider[TuringMetaConfig, TuringConfig, TuringGame]):
    @override
    def create_game(self, *, meta_config: TuringMetaConfig, config: TuringConfig) -> TuringGame:
        with get_db_cursor(data_file=meta_config.data_file) as cur:
            card_id: int
            key: int
            code: int

            card_id, key, code = cur.execute(
                f"SELECT card_id, key, code FROM game_{config.num_verifiers} WHERE game_id = ?",
                (config.game_id,),
            ).fetchone()

        return TuringGame(
            code=code,
            verifiers=[
                meta_config.card_pool[i]
                for i in self.unpack(data=card_id, base=64, n=config.num_verifiers)
            ],
            keys=self.unpack(data=key, base=16, n=config.num_verifiers),
            max_guesses=config.max_guesses,
        )

    @staticmethod
    def unpack(*, data: int, base: int, n: int) -> list[int]:
        buf: list[int] = []

        for _ in range(n):
            buf.append(data % base)
            data //= base

        return buf[::-1]

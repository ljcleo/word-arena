from collections.abc import Callable
from pathlib import Path
from random import Random
from typing import Any, override

from pydantic import BaseModel, TypeAdapter

from ....utils import get_db_cursor


class TuringMetaConfig(BaseModel):
    data_file: Path

    @override
    def model_post_init(self, context: Any) -> None:
        with get_db_cursor(data_file=self.data_file) as cur:
            self._card_pool: dict[int, list[str]] = {
                card_id: TypeAdapter(list[str]).validate_json(card)
                for card_id, card in cur.execute("SELECT card_id, card FROM card")
            }

            self._game_pool: dict[int, list[int]] = {
                num_verifiers: [
                    game_id
                    for (game_id,) in cur.execute(f"SELECT game_id FROM game_{num_verifiers}")
                ]
                for (num_verifiers,) in cur.execute(
                    "SELECT CAST(SUBSTR(name, 6) AS INTEGER) AS num_verifiers FROM sqlite_master "
                    "WHERE name LIKE 'game\\__%' ESCAPE '\\' ORDER BY num_verifiers"
                ).fetchall()
            }

    @property
    def card_pool(self) -> dict[int, list[str]]:
        return dict(self._card_pool)

    @property
    def num_verifiers_pool(self) -> list[int]:
        return sorted(self._game_pool.keys())

    def select_game_id(self, *, num_verifiers: int, selector: Callable[[int], int]) -> int:
        game_pool: list[int] = self._game_pool[num_verifiers]
        return game_pool[selector(len(game_pool))]

    def random_game_id(self, *, num_verifiers: int, rng: Random) -> int:
        return rng.choice(self._game_pool[num_verifiers])


class TuringMutableMetaConfig(BaseModel):
    num_verifiers: int
    max_turns: int

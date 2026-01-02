from typing import override

from ....common.generator.provider import BaseGameProvider
from ....common.utils import get_db_cursor
from ..game import StrandsGame
from .common import StrandsConfig, StrandsGameData, StrandsMetaConfig


class StrandsGameProvider(BaseGameProvider[StrandsMetaConfig, StrandsConfig, StrandsGame]):
    @override
    def create_game(self, *, meta_config: StrandsMetaConfig, config: StrandsConfig) -> StrandsGame:
        with get_db_cursor(data_file=meta_config.data_file) as cur:
            data: StrandsGameData = StrandsGameData.model_validate_json(
                cur.execute(
                    "SELECT board FROM game WHERE game_id = ?", (config.game_id,)
                ).fetchone()[0]
            )

        return StrandsGame(board=data.board, clue=data.clue, max_guesses=config.max_guesses)

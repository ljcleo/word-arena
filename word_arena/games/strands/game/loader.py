from typing import override

from ....common.game.loader.base import BaseGameLoader
from ....utils import get_db_cursor
from ..common import StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo
from .common import StrandsConfig, StrandsGameData
from .engine import StrandsGameEngine


class StrandsGameLoader(
    BaseGameLoader[StrandsConfig, StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult]
):
    @override
    def create_engine(self, *, config: StrandsConfig) -> StrandsGameEngine:
        with get_db_cursor(data_file=config.data_file) as cur:
            data: StrandsGameData = StrandsGameData.model_validate_json(
                cur.execute(
                    "SELECT board FROM game WHERE game_id = ?", (config.game_id,)
                ).fetchone()[0]
            )

        return StrandsGameEngine(board=data.board, clue=data.clue, max_turns=config.max_turns)

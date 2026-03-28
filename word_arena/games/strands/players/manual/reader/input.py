from collections.abc import Callable
from typing import override

from pydantic import BaseModel

from ......common.game.common import Trajectory
from ......players.manual.reader.input import BaseInputManualReader
from ....common import StrandsFeedback, StrandsGuess, StrandsInfo


class StrandsInputPromptConfig(BaseModel):
    row: str
    column: str
    add: str


class StrandsInputManualReader(
    BaseInputManualReader[StrandsInputPromptConfig, StrandsInfo, StrandsGuess, StrandsFeedback]
):
    @override
    def input_guess(
        self,
        *,
        trajectory: Trajectory[StrandsInfo, StrandsGuess, StrandsFeedback],
        input_func: Callable[[str], str],
    ) -> StrandsGuess:
        turn_id: int = len(trajectory.turns) + 1
        coords: list[tuple[int, int]] = []

        while True:
            coord_id: int = len(coords) + 1
            row: str = input_func(self.prompt_config.row.format(turn_id=turn_id, coord_id=coord_id))

            column: str = input_func(
                self.prompt_config.column.format(turn_id=turn_id, coord_id=coord_id)
            )

            coords.append(
                (int(row) if row.isdigit() else -1, int(column) if column.isdigit() else -1)
            )

            if input_func(self.prompt_config.add.format(turn_id=turn_id)).strip().lower()[0] != "y":
                break

        return StrandsGuess(coords=coords)

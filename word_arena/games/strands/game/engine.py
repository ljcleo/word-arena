from typing import override

from pydantic import BaseModel

from ....common.game.engine.base import BaseGameEngine
from ....common.game.state import GameStateInterface
from ....utils import get_db_cursor
from ..common import (
    StrandsConfig,
    StrandsError,
    StrandsFeedback,
    StrandsFinalResult,
    StrandsGuess,
    StrandsInfo,
)


class StrandsGameEngine(
    BaseGameEngine[StrandsConfig, StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult]
):
    _DIR_MAP: dict[tuple[int, int], int] = {
        coord: index
        for index, coord in enumerate(
            ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))
        )
    }

    _DIR_OFFSET: list[int] = [6, 7, 1, -5, -6, -7, -1, 5]

    def __init__(self, *, config: StrandsConfig) -> None:
        class StrandsGameData(BaseModel):
            board: list[tuple[str, int]]
            clue: str

        with get_db_cursor(data_file=config.data_file) as cur:
            data: StrandsGameData = StrandsGameData.model_validate_json(
                cur.execute(
                    "SELECT board FROM game WHERE game_id = ?", (config.game_id,)
                ).fetchone()[0],
                strict=True,
            )

        self._board: list[tuple[str, int]] = data.board
        self._clue: str = data.clue
        self._max_turns: int = config.max_turns

        self._2d_board: list[str] = [
            "".join(self._board[x * 6 + y][0] for y in range(6)) for x in range(8)
        ]

        self._is_start: list[bool] = [True for _ in range(len(self._board))]
        self._end_indices: dict[int, int] = {}
        self._num_targets: int = 1

        for pos, (_, dir) in enumerate(self._board):
            if dir < 8:
                self._is_start[pos + self._DIR_OFFSET[dir]] = False
            elif dir == 8:
                self._end_indices[pos] = self._num_targets
                self._num_targets += 1
            else:
                self._end_indices[pos] = 0

    @override
    def start_game(self) -> StrandsInfo:
        self._visited: dict[int, bool] = {pos: False for pos in range(len(self._board))}
        self._found_indices: set[int] = set()
        return StrandsInfo(board=self._2d_board, clue=self._clue, max_turns=self._max_turns)

    @override
    def is_over(
        self,
        *,
        state: GameStateInterface[StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult],
    ) -> bool:
        num_remains: int = self._num_targets - len(self._found_indices)
        return num_remains == 0 or len(state.turns) + num_remains > self._max_turns > 0

    @override
    def process_guess(self, *, guess: StrandsGuess) -> StrandsFeedback:
        coords: list[tuple[int, int]] = guess.coords

        if len(coords) == 0:
            return StrandsError.EMPTY

        coords_pos: list[int] = [x * 6 + y for x, y in coords]

        coords_diff: list[tuple[int, int]] = [
            (coords[index + 1][0] - coords[index][0], coords[index + 1][1] - coords[index][1])
            for index in range(len(coords) - 1)
        ]

        for x, y in coords:
            if not (0 <= x < 8 and 0 <= y < 6):
                return StrandsError.OUT_OF_BOUNDS

        for diff in coords_diff:
            if diff not in self._DIR_MAP:
                return StrandsError.NOT_CONTINUOUS

        if len(set(coords)) != len(coords):
            return StrandsError.OVERLAP

        for pos in coords_pos:
            if self._visited[pos]:
                return StrandsError.USED

        start_match: bool = self._is_start[coords_pos[0]]
        code: int = 0

        for index in range(len(coords)):
            pos: int = coords_pos[index]

            if index < len(coords) - 1:
                if self._DIR_MAP[coords_diff[index]] != self._board[pos][1]:
                    break
            else:
                if start_match and self._board[pos][1] >= 8:
                    self._found_indices.add(self._end_indices[pos])
                    code = self._board[pos][1] - 7

        if code > 0:
            for pos in coords_pos:
                self._visited[pos] = True

        return code

    @override
    def get_final_result(self) -> StrandsFinalResult:
        return StrandsFinalResult(found_indices=self._found_indices, answers=self._build_answers())

    def _build_answers(self) -> list[tuple[str, list[tuple[int, int]]]]:
        buffer: dict[int, tuple[str, list[tuple[int, int]]]] = {}
        vis: list[bool] = [False for _ in self._board]

        for pos in range(len(self._board)):
            if self._is_start[pos]:
                cur: int = pos
                word: str = ""
                coords: list[tuple[int, int]] = []

                while self._board[cur][1] < 8:
                    assert not vis[cur]
                    vis[cur] = True
                    word += self._board[cur][0]
                    coords.append((cur // 6, cur % 6))
                    cur += self._DIR_OFFSET[self._board[cur][1]]

                assert not vis[cur]
                vis[cur] = True
                coords.append((cur // 6, cur % 6))
                buffer[self._end_indices[cur]] = word + self._board[cur][0], coords

        return [buffer[index] for index in range(len(buffer))]

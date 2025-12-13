from typing import TypedDict


class GameResult[GT, PT, AT, RT, FT](TypedDict):
    game_info: GT
    trajectory: list[tuple[PT, AT, RT]]
    summary: FT

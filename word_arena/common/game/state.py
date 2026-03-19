from .common import GameStatus, Trajectory, Turn


class GameState[IT, GT, FT, RT]:
    def __init__(self) -> None:
        self._status: GameStatus = GameStatus.PRE

    @property
    def status(self) -> GameStatus:
        return self._status

    @property
    def trajectory(self) -> Trajectory[IT, GT, FT]:
        return self._trajectory

    @property
    def game_info(self) -> IT:
        return self.trajectory.game_info

    @property
    def turns(self) -> list[Turn[GT, FT]]:
        return self.trajectory.turns

    @property
    def final_result(self) -> RT:
        return self._final_result

    def reset(self, *, game_info: IT) -> None:
        assert self.status == GameStatus.PRE
        self._status = GameStatus.IN
        self._trajectory: Trajectory[IT, GT, FT] = Trajectory(game_info=game_info, turns=[])

    def add_turn(self, *, turn: Turn[GT, FT]) -> None:
        assert self.status == GameStatus.IN
        self.turns.append(turn)

    def end(self, *, final_result: RT) -> None:
        assert self.status == GameStatus.IN
        self._status = GameStatus.POST
        self._final_result: RT = final_result


class GameStateInterface[IT, GT, FT, RT]:
    def __init__(self, *, state: GameState[IT, GT, FT, RT]) -> None:
        self._state: GameState[IT, GT, FT, RT] = state

    @property
    def status(self) -> GameStatus:
        return self._state.status

    @property
    def trajectory(self) -> Trajectory[IT, GT, FT]:
        return self._state.trajectory

    @property
    def game_info(self) -> IT:
        return self.trajectory.game_info

    @property
    def turns(self) -> list[Turn[GT, FT]]:
        return self.trajectory.turns

    @property
    def final_result(self) -> RT:
        return self._state.final_result

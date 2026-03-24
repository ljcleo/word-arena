from ...common.game.common import Trajectory, Turn


class ManualGameState[IT, GT, FT]:
    @property
    def trajectory(self) -> Trajectory[IT, GT, FT]:
        return self._trajectory

    @property
    def game_info(self) -> IT:
        return self.trajectory.game_info

    @property
    def turns(self) -> list[Turn[GT, FT]]:
        return self.trajectory.turns

    def reset(self, *, game_info: IT) -> None:
        self._trajectory: Trajectory[IT, GT, FT] = Trajectory(game_info=game_info, turns=[])

    def add_turn(self, *, turn: Turn[GT, FT]) -> None:
        self.trajectory.turns.append(turn)


class ManualGameStateInterface[IT, GT, FT]:
    def __init__(self, *, game_state: ManualGameState[IT, GT, FT]) -> None:
        self._game_state: ManualGameState[IT, GT, FT] = game_state

    @property
    def trajectory(self) -> Trajectory[IT, GT, FT]:
        return self._game_state.trajectory

    @property
    def game_info(self) -> IT:
        return self.trajectory.game_info

    @property
    def turns(self) -> list[Turn[GT, FT]]:
        return self.trajectory.turns

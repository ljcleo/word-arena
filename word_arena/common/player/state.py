from ...common.game.common import Trajectory, Turn
from .common import GameRecord, GameSummary


class PlayerGameState[IT, AT, GT, FT, RT]:
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
    def last_analysis(self) -> AT | None:
        return self._last_analysis

    @property
    def final_result(self) -> RT:
        return self._final_result

    @property
    def game_record(self) -> GameRecord[IT, AT, GT, FT, RT]:
        return GameRecord(
            trajectory=self.trajectory,
            last_analysis=self.last_analysis,
            final_result=self.final_result,
        )

    def reset(self, *, game_info: IT) -> None:
        self._trajectory: Trajectory[IT, GT, FT] = Trajectory(game_info=game_info, turns=[])
        self._last_analysis: AT | None = None

    def update_analysis(self, *, analysis: AT | None) -> None:
        self._last_analysis = analysis

    def add_turn(self, *, turn: Turn[GT, FT]) -> None:
        self.trajectory.turns.append(turn)

    def end(self, *, final_result: RT) -> None:
        self._final_result: RT = final_result


class PlayerNoteState[NT, IT, AT, GT, FT, RT, ST]:
    @property
    def note(self) -> NT:
        return self._note

    @property
    def history(self) -> list[GameSummary[IT, AT, GT, FT, RT, ST]]:
        return self._history

    def set_note(self, *, note: NT) -> None:
        self._note: NT = note
        self._history: list[GameSummary[IT, AT, GT, FT, RT, ST]] = []

    def add_game_summary(self, *, game_summary: GameSummary[IT, AT, GT, FT, RT, ST]) -> None:
        self._history.append(game_summary)


class PlayerGameStateInterface[IT, AT, GT, FT, RT]:
    def __init__(self, *, game_state: PlayerGameState[IT, AT, GT, FT, RT]) -> None:
        self._game_state: PlayerGameState[IT, AT, GT, FT, RT] = game_state

    @property
    def trajectory(self) -> Trajectory[IT, GT, FT]:
        return self._game_state.trajectory

    @property
    def game_info(self) -> IT:
        return self.trajectory.game_info

    @property
    def turns(self) -> list[Turn[GT, FT]]:
        return self.trajectory.turns

    @property
    def last_analysis(self) -> AT | None:
        return self._game_state.last_analysis

    @property
    def final_result(self) -> RT:
        return self._game_state.final_result

    @property
    def game_record(self) -> GameRecord[IT, AT, GT, FT, RT]:
        return self._game_state.game_record


class PlayerNoteStateInterface[NT, IT, AT, GT, FT, RT, ST]:
    def __init__(self, *, note_state: PlayerNoteState[NT, IT, AT, GT, FT, RT, ST]) -> None:
        self._note_state: PlayerNoteState[NT, IT, AT, GT, FT, RT, ST] = note_state

    @property
    def note(self) -> NT:
        return self._note_state.note

    @property
    def history(self) -> list[GameSummary[IT, AT, GT, FT, RT, ST]]:
        return self._note_state.history

from ..game.common import GuessFeedback, Turn
from ..game.game import Game
from .common import AnalyzedGuess, GameSummary
from .engine.base import BasePlayerEngine
from .renderer.base import BasePlayerRenderer
from .state import (
    PlayerGameState,
    PlayerGameStateInterface,
    PlayerNoteState,
    PlayerNoteStateInterface,
)


class Player[NT, IT, AT, GT, FT, RT, ST]:
    def __init__(
        self,
        *,
        engine: BasePlayerEngine[NT, IT, AT, GT, FT, RT, ST],
        renderer: BasePlayerRenderer[NT, IT, AT, GT, FT, RT, ST],
    ) -> None:
        self._engine: BasePlayerEngine[NT, IT, AT, GT, FT, RT, ST] = engine
        self._renderer: BasePlayerRenderer[NT, IT, AT, GT, FT, RT, ST] = renderer

        self._note_state: PlayerNoteState[NT, IT, AT, GT, FT, RT, ST] = PlayerNoteState()
        self._game_state: PlayerGameState[IT, AT, GT, FT, RT] = PlayerGameState()

        self._ro_note_state: PlayerNoteStateInterface[NT, IT, AT, GT, FT, RT, ST] = (
            PlayerNoteStateInterface(note_state=self._note_state)
        )

        self._ro_game_state: PlayerGameStateInterface[IT, AT, GT, FT, RT] = (
            PlayerGameStateInterface(game_state=self._game_state)
        )

    @property
    def note_state(self) -> PlayerNoteStateInterface[NT, IT, AT, GT, FT, RT, ST]:
        return self._ro_note_state

    @property
    def game_state(self) -> PlayerGameStateInterface[IT, AT, GT, FT, RT]:
        return self._ro_game_state

    def setup(self) -> None:
        self._note_state.set_note(note=self._engine.create_note())
        self._renderer.render_note(note_state=self.note_state)

    def play(self, *, game: Game[IT, GT, FT, RT]) -> None:
        game_info: IT | None = game.start()
        assert game_info is not None
        self._game_state.reset(game_info=game_info)

        while True:
            analyzed_guess: AnalyzedGuess[AT, GT] = self._engine.analyze_and_guess(
                note_state=self.note_state, game_state=self.game_state
            )

            self._game_state.update_analysis(analysis=analyzed_guess.analysis)
            self._renderer.render_last_analysis(game_state=self.game_state)
            guess_feedback: GuessFeedback[FT] | None = game.guess(guess=analyzed_guess.guess)
            assert guess_feedback is not None

            self._game_state.add_turn(
                turn=Turn(guess=analyzed_guess.guess, feedback=guess_feedback.feedback)
            )

            if guess_feedback.is_over:
                break

        final_result: RT | None = game.query()
        assert final_result is not None
        self._game_state.end(final_result=final_result)

        game_summary: GameSummary[IT, AT, GT, FT, RT, ST] = GameSummary(
            game_record=self.game_state.game_record,
            reflection=self._engine.summarize_and_reflect(
                note_state=self.note_state, game_state=self.game_state
            ),
        )

        self._renderer.render_reflection(reflection=game_summary.reflection)
        self._note_state.add_game_summary(game_summary=game_summary)

    def evolve(self) -> None:
        self._note_state.set_note(note=self._engine.update_note(note_state=self.note_state))
        self._renderer.render_note(note_state=self.note_state)

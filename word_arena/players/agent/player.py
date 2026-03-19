from typing import override

from ...common.game.common import Turn
from ...common.player.base import BasePlayer
from .common import AnalyzedGuess, GameSummary
from .engine.base import BaseAgentEngine
from .renderer.base import BaseAgentRenderer
from .state import AgentGameState, AgentGameStateInterface, AgentNoteState, AgentNoteStateInterface


class AgentPlayer[IT, GT, FT, RT, NT](BasePlayer[IT, GT, FT, RT]):
    def __init__(
        self,
        *,
        engine: BaseAgentEngine[IT, GT, FT, RT, NT],
        renderer: BaseAgentRenderer[IT, GT, FT, RT, NT],
    ):
        self._engine: BaseAgentEngine[IT, GT, FT, RT, NT] = engine
        self._renderer: BaseAgentRenderer[IT, GT, FT, RT, NT] = renderer

        self._note_state: AgentNoteState[IT, GT, FT, RT, NT] = AgentNoteState()
        self._game_state: AgentGameState[IT, GT, FT, RT] = AgentGameState()

        self._ro_note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT] = AgentNoteStateInterface(
            note_state=self._note_state
        )

        self._ro_game_state: AgentGameStateInterface[IT, GT, FT, RT] = AgentGameStateInterface(
            game_state=self._game_state
        )

        self._note_state.set_note(note=self._engine.create_note())
        self._renderer.render_note(note_state=self.note_state)

    @property
    def note_state(self) -> AgentNoteStateInterface[IT, GT, FT, RT, NT]:
        return self._ro_note_state

    @property
    def game_state(self) -> AgentGameStateInterface[IT, GT, FT, RT]:
        return self._ro_game_state

    @override
    def prepare(self, *, game_info: IT) -> None:
        self._game_state.reset(game_info=game_info)

    @override
    def guess(self) -> GT:
        analyzed_guess: AnalyzedGuess[GT] = self._engine.analyze_and_guess(
            note_state=self.note_state, game_state=self.game_state
        )

        self._game_state.update_analysis(analysis=analyzed_guess.analysis)
        self._renderer.render_last_analysis(game_state=self.game_state)
        return analyzed_guess.guess

    @override
    def digest(self, *, guess: GT, feedback: FT) -> None:
        self._game_state.add_turn(turn=Turn(guess=guess, feedback=feedback))

    @override
    def reflect(self, *, final_result: RT) -> None:
        self._game_state.end(final_result=final_result)

        game_summary: GameSummary[IT, GT, FT, RT] = self._engine.summarize_and_reflect(
            note_state=self.note_state, game_state=self.game_state
        )

        self._renderer.render_reflection(reflection=game_summary.reflection)
        self._note_state.add_game_summary(game_summary=game_summary)

    @override
    def evolve(self) -> None:
        self._note_state.set_note(note=self._engine.update_note(note_state=self.note_state))

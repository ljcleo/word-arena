from typing import Any

from .common import GameStatus, GuessFeedback, Turn
from .engine.base import BaseGameEngine
from .renderer.base import BaseGameRenderer
from .state import GameState, GameStateInterface


class Game[IT, GT, FT, RT]:
    def __init__(
        self,
        *,
        engine: BaseGameEngine[Any, IT, GT, FT, RT],
        renderer: BaseGameRenderer[IT, GT, FT, RT],
    ) -> None:
        self._engine: BaseGameEngine[Any, IT, GT, FT, RT] = engine
        self._renderer: BaseGameRenderer[IT, GT, FT, RT] = renderer

        self._state: GameState[IT, GT, FT, RT] = GameState()
        self._ro_state: GameStateInterface[IT, GT, FT, RT] = GameStateInterface(state=self._state)

    @property
    def state(self) -> GameStateInterface[IT, GT, FT, RT]:
        return self._ro_state

    def start(self) -> IT | None:
        if self.state.status != GameStatus.PRE:
            return None

        self._state.reset(game_info=self._engine.start_game())
        self._renderer.render_game_info(state=self.state)
        return self.state.game_info

    def guess(self, *, guess: GT) -> GuessFeedback[FT] | None:
        if self.state.status != GameStatus.IN:
            return None

        self._renderer.render_guess(state=self.state, guess=guess)
        feedback: FT = self._engine.process_guess(guess=guess)
        self._state.add_turn(turn=Turn(guess=guess, feedback=feedback))
        self._renderer.render_last_feedback(state=self.state)

        if self._engine.is_over(state=self.state):
            self._state.end(final_result=self._engine.get_final_result())
            self._renderer.render_final_result(state=self.state)

        return GuessFeedback(feedback=feedback, is_over=self.state.status == GameStatus.POST)

    def query(self) -> RT | None:
        return self.state.final_result if self.state.status == GameStatus.POST else None

from abc import ABC, abstractmethod

from ..game.common import GuessFeedback
from ..game.game import Game


class BasePlayer[IT, GT, FT, RT](ABC):
    def play(self, *, game: Game[IT, GT, FT, RT]) -> None:
        game_info: IT | None = game.start()
        assert game_info is not None
        self.prepare(game_info=game_info)

        while True:
            guess: GT = self.guess()
            guess_feedback: GuessFeedback[FT] | None = game.guess(guess=guess)
            assert guess_feedback is not None
            self.digest(guess=guess, feedback=guess_feedback.feedback)

            if guess_feedback.is_over:
                break

        final_result: RT | None = game.query()
        assert final_result is not None
        self.reflect(final_result=final_result)

    @abstractmethod
    def prepare(self, *, game_info: IT) -> None: ...

    @abstractmethod
    def guess(self) -> GT: ...

    @abstractmethod
    def digest(self, *, guess: GT, feedback: FT) -> None: ...

    @abstractmethod
    def reflect(self, *, final_result: RT) -> None: ...

    @abstractmethod
    def evolve(self) -> None: ...

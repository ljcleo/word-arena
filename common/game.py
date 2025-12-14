from abc import ABC, abstractmethod

from common.common import GameResult
from common.player import BasePlayer


class BaseGame[GT, PT, AT, RT, FT](ABC):
    def play(self, *, player: BasePlayer[GT, PT, AT, RT]) -> GameResult[GT, PT, AT, RT, FT]:
        game_info: GT = self.start_game()
        player.prepare(game_info=game_info)
        trajectory: list[tuple[PT, AT, RT]] = []

        while not self.is_over():
            hint: PT = self.get_guess_prompt()
            guess: AT = player.guess(hint=hint)
            result: RT = self.process_guess(guess=guess)
            trajectory.append((hint, guess, result))
            player.digest(hint=hint, guess=guess, result=result)

        return {"game_info": game_info, "trajectory": trajectory, "summary": self.summarize_game()}

    @abstractmethod
    def start_game(self) -> GT:
        raise NotImplementedError()

    @abstractmethod
    def is_over(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def get_guess_prompt(self) -> PT:
        raise NotImplementedError()

    @abstractmethod
    def process_guess(self, *, guess: AT) -> RT:
        raise NotImplementedError()

    @abstractmethod
    def summarize_game(self) -> FT:
        raise NotImplementedError()

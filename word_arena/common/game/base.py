from abc import ABC, abstractmethod

from ..player.base import BasePlayer


class BaseGame[IT, HT, GT, FT, RT](ABC):
    def play(self, *, player: BasePlayer[IT, HT, GT, FT]) -> RT:
        game_info: IT = self.start_game()
        player.prepare(game_info=game_info)

        while not self.is_over():
            hint: HT = self.get_guess_prompt()
            guess: GT = player.guess(hint=hint)
            feedback: FT = self.process_guess(guess=guess)
            player.digest(hint=hint, guess=guess, feedback=feedback)

        return self.get_final_result()

    @abstractmethod
    def start_game(self) -> IT:
        raise NotImplementedError()

    @abstractmethod
    def is_over(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def get_guess_prompt(self) -> HT:
        raise NotImplementedError()

    @abstractmethod
    def process_guess(self, *, guess: GT) -> FT:
        raise NotImplementedError()

    @abstractmethod
    def get_final_result(self) -> RT:
        raise NotImplementedError()

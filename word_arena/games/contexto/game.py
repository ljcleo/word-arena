from collections.abc import Sequence
from datetime import date
from random import Random
from typing import override

import httpx

from ...common.game.base import BaseGame
from .common import (
    ContextoError,
    ContextoFeedback,
    ContextoFinalResult,
    ContextoGuess,
    ContextoResponse,
)


class ContextoGame(BaseGame[int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult]):
    def __init__(self, *, game_id: int, max_guesses: int) -> None:
        self._game_id: int = game_id
        self._max_guesses: int = max_guesses
        self._base_url: str = "https://api.contexto.me/machado/en"

    @override
    def start_game(self) -> int:
        self._best_pos: int = 1 << 32
        self._best_word: str = "(N/A)"
        self._num_guesses: int = 0
        return self._max_guesses

    @override
    def is_over(self) -> bool:
        return self._best_pos == 0 or self._num_guesses >= self._max_guesses > 0

    @override
    def get_guess_prompt(self) -> None:
        pass

    @override
    def process_guess(self, *, guess: ContextoGuess) -> ContextoFeedback:
        self._num_guesses += 1
        word: str = guess.word

        if not (word.isalpha() and word.islower()):
            return ContextoError(error="Your guess should only contain lowercase letters")

        response: httpx.Response = httpx.get(f"{self._base_url}/game/{self._game_id}/{word}")

        if response.status_code == 200:
            feedback: ContextoResponse = ContextoResponse.model_validate_json(response.content)

            if feedback.distance < self._best_pos:
                self._best_pos = feedback.distance
                self._best_word = feedback.lemma

            return feedback
        elif response.status_code == 404:
            return ContextoError.model_validate_json(response.content)
        else:
            raise RuntimeError(f"Status code {response.status_code}")

    @override
    def get_final_result(self) -> ContextoFinalResult:
        return ContextoFinalResult(
            best_pos=self._best_pos,
            best_word=self._best_word,
            top_words=httpx.get(f"{self._base_url}/top/{self._game_id}").json()["words"],
        )


class ContextoGameManager:
    def __init__(self, *, seed: int) -> None:
        self._max_games: int = (date.today() - date(2022, 9, 18)).days
        self._rng: Random = Random(seed)

    def create_game(self, *, game_id: int, max_guesses: int) -> ContextoGame:
        return ContextoGame(game_id=game_id, max_guesses=max_guesses)

    def create_random_game(self, *, param_candidates: Sequence[int]) -> ContextoGame:
        game_id: int = self._rng.randrange(self._max_games + 1)
        max_guesses: int = self._rng.choice(param_candidates)
        return self.create_game(game_id=game_id, max_guesses=max_guesses)

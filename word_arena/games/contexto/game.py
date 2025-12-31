from logging import WARNING, getLogger
from typing import override
from urllib.parse import quote

from httpx import Response, get
from tenacity import before_sleep_log, retry, wait_random

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

        return self._fetch_feedback(word=word)

    @override
    def get_final_result(self) -> ContextoFinalResult:
        return ContextoFinalResult(
            best_pos=self._best_pos, best_word=self._best_word, top_words=self._fetch_top_words()
        )

    @retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
    def _fetch_feedback(self, *, word: str) -> ContextoFeedback:
        response: Response = get(quote(f"{self._base_url}/game/{self._game_id}/{word}"))

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

    @retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
    def _fetch_top_words(self) -> list[str]:
        return get(quote(f"{self._base_url}/top/{self._game_id}")).json()["words"]

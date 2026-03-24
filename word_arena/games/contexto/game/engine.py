from logging import WARNING, getLogger
from typing import override

from httpx import Response, get
from tenacity import before_sleep_log, retry, wait_random

from ....common.game.engine.base import BaseGameEngine
from ..common import (
    ContextoConfig,
    ContextoError,
    ContextoFeedback,
    ContextoFinalResult,
    ContextoGuess,
    ContextoResponse,
)
from .state import ContextoGameStateInterface


class ContextoGameEngine(
    BaseGameEngine[ContextoConfig, int, ContextoGuess, ContextoFeedback, ContextoFinalResult]
):
    def __init__(self, *, config: ContextoConfig) -> None:
        self._base_url: str = config.base_url
        self._game_id: int = config.game_id
        self._max_turns: int = config.max_turns

    @override
    def start_game(self) -> int:
        self._best_pos: int = 1 << 32
        self._best_word: str = "(N/A)"
        return self._max_turns

    @override
    def is_over(self, *, state: ContextoGameStateInterface) -> bool:
        return self._best_pos == 0 or len(state.turns) >= self._max_turns > 0

    @override
    def process_guess(self, *, guess: ContextoGuess) -> ContextoFeedback:
        word: str = guess.word
        if not (word.isalpha() and word.islower()):
            return ContextoError(error=None)

        return self._fetch_feedback(word=word)

    @override
    def get_final_result(self) -> ContextoFinalResult:
        return ContextoFinalResult(
            best_pos=self._best_pos, best_word=self._best_word, top_words=self._fetch_top_words()
        )

    @retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
    def _fetch_feedback(self, *, word: str) -> ContextoFeedback:
        response: Response = get(f"{self._base_url}/game/{self._game_id}/{word}")

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
        return get(f"{self._base_url}/top/{self._game_id}").json()["words"]

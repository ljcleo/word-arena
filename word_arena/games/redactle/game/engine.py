from collections import defaultdict
from typing import override

from pydantic import BaseModel

from ....common.game.engine.base import BaseGameEngine
from ....utils import get_db_cursor
from ..common import (
    RedactleConfig,
    RedactleFeedback,
    RedactleFinalResult,
    RedactleGuess,
    RedactleInfo,
    RedactleResponse,
)
from .state import RedactleGameStateInterface


class RedactleGameEngine(
    BaseGameEngine[
        RedactleConfig, RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult
    ]
):
    def __init__(self, *, config: RedactleConfig) -> None:
        class RedactleGameData(BaseModel):
            article: list[list[tuple[str, str | None]]]
            lemma_map: dict[str, str]

        with get_db_cursor(data_file=config.data_file) as cur:
            data: RedactleGameData = RedactleGameData.model_validate_json(
                cur.execute(
                    "SELECT data FROM game WHERE game_id = ?", (config.game_id,)
                ).fetchone()[0]
            )

        self._article: list[list[tuple[str, str | None]]] = data.article
        self._lemma_map: dict[str, str] = data.lemma_map
        self._stop_words: set[str] = config.stop_words
        self._max_turns: int = config.max_turns
        self._title: str = "".join(word for word, _ in self._article[0])

        self._title_words: set[str] = {
            word
            for _, word in self._article[0]
            if word is not None and word not in self._stop_words
        }

        self._num_targets: int = len(self._title_words)
        self._positions: defaultdict[str, list[tuple[int, int]]] = defaultdict(list)

        for line_index, line in enumerate(self._article):
            for word_index, (_, word) in enumerate(line):
                if word is not None:
                    self._positions[word].append((line_index, word_index))

    @override
    def start_game(self) -> RedactleInfo:
        self._found_words: set[str] = set()

        return RedactleInfo(
            article=self._article, stop_words=self._stop_words, max_turns=self._max_turns
        )

    @override
    def is_over(self, *, state: RedactleGameStateInterface) -> bool:
        num_remains: int = self._num_targets - len(self._found_words)
        return num_remains == 0 or len(state.turns) + num_remains > self._max_turns > 0

    @override
    def process_guess(self, *, guess: RedactleGuess) -> RedactleFeedback:
        word: str = guess.word.lower()
        if any(c.isspace() for c in word):
            return False

        lemma: str = self._lemma_map.get(word, word)

        if lemma in self._stop_words:
            return True
        elif lemma in self._title_words:
            self._found_words.add(lemma)

        return RedactleResponse(word=word, lemma=lemma, positions=self._positions[lemma])

    @override
    def get_final_result(self) -> RedactleFinalResult:
        return RedactleFinalResult(
            found_words=self._found_words, title=self._title, title_words=self._title_words
        )

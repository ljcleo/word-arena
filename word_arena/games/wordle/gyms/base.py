from pathlib import Path
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo
from ..formatters.base import WordleFinalResultFormatter
from ..generators.common import WordleConfig


class WordleConfigGym[**P](
    BaseConfigGym[
        WordleConfig, WordleInfo, None, WordleGuess, WordleFeedback, WordleFinalResult, P
    ],
    WordleFinalResultFormatter,
):
    def __init__(self, *, word_list_file: Path) -> None:
        with word_list_file.open(encoding="utf8") as f:
            self._word_list: list[str] = list(map(str.strip, f))

    @override
    def create_config(self) -> WordleConfig:
        return WordleConfig(
            word_list=self._word_list,
            target_ids=[
                int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))
            ],
            max_guesses=int(input("Max Guesses: ")),
        )

from pathlib import Path
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo
from ..formatters.base import LetrosoFinalResultFormatter
from ..generators.common import LetrosoConfig


class LetrosoConfigGym[**P](
    BaseConfigGym[
        LetrosoConfig, LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult, P
    ]
):
    def __init__(self, *, word_list_file: Path) -> None:
        with word_list_file.open(encoding="utf8") as f:
            self._word_list: list[str] = list(map(str.strip, f))

    @override
    def create_config(self) -> LetrosoConfig:
        return LetrosoConfig(
            word_list=self._word_list,
            target_ids=[
                int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))
            ],
            max_letters=int(input("Max Input Letters: ")),
            max_guesses=int(input("Max Guesses: ")),
        )

    @override
    @staticmethod
    def get_final_result_formatter_cls() -> type[LetrosoFinalResultFormatter]:
        return LetrosoFinalResultFormatter

from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import ContextoHintGuess
from ..formatters.base import ContextoHintFinalResultFormatter
from ..generators.common import ContextoHintConfig


class ContextoHintConfigGym[**P](
    BaseConfigGym[ContextoHintConfig, None, list[str], ContextoHintGuess, int, list[str], P]
):
    @override
    def create_config(self) -> ContextoHintConfig:
        return ContextoHintConfig(
            game_id=int(input("Game ID: ")), num_candidates=int(input("Number of Candidates: "))
        )

    @override
    @staticmethod
    def get_final_result_formatter_cls() -> type[ContextoHintFinalResultFormatter]:
        return ContextoHintFinalResultFormatter

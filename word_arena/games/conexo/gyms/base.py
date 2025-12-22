from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo
from ..formatters.base import ConexoFinalResultFormatter
from ..generators.common import ConexoConfig


class ConexoConfigGym[**P](
    BaseConfigGym[ConexoConfig, ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoFinalResult, P]
):
    @override
    def create_config(self) -> ConexoConfig:
        return ConexoConfig(
            game_id=int(input("Game ID: ")), max_guesses=int(input("Max Guesses: "))
        )

    @override
    @staticmethod
    def get_final_result_formatter_cls() -> type[ConexoFinalResultFormatter]:
        return ConexoFinalResultFormatter

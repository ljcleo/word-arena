from ....common.gym.base import BaseConfigGym
from ..common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo
from ..formatters.base import ConexoFinalResultFormatter
from ..generators.common import ConexoConfig


class ConexoConfigGym[**P](
    BaseConfigGym[
        ConexoConfig, ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoFinalResult, P
    ],
    ConexoFinalResultFormatter,
):
    pass

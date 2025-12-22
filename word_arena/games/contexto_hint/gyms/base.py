from ....common.gym.base import BaseConfigGym
from ..common import ContextoHintGuess
from ..formatters.base import ContextoHintFinalResultFormatter
from ..generators.common import ContextoHintConfig


class ContextoHintConfigGym[**P](
    BaseConfigGym[ContextoHintConfig, None, list[str], ContextoHintGuess, int, list[str], P],
    ContextoHintFinalResultFormatter,
):
    pass

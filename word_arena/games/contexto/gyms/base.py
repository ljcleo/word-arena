from ....common.gym.base import BaseConfigGym
from ..common import ContextoFeedback, ContextoFinalResult, ContextoGuess
from ..formatters.base import ContextoFinalResultFormatter
from ..generators.common import ContextoConfig


class ContextoConfigGym[**P](
    BaseConfigGym[
        ContextoConfig, int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult, P
    ],
    ContextoFinalResultFormatter,
):
    pass

from ....common.gym.base import BaseConfigGym
from ..common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo
from ..formatters.base import LetrosoFinalResultFormatter
from ..generators.common import LetrosoConfig


class LetrosoConfigGym[**P](
    BaseConfigGym[
        LetrosoConfig, LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult, P
    ],
    LetrosoFinalResultFormatter,
):
    pass

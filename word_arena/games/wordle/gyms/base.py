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
    pass

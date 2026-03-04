from typing import override

from ....common.player.manual import BaseManualPlayer
from ..common import TuringFeedback, TuringGuess, TuringInfo
from ..formatters.base import TuringInGameFormatter


class TuringManualPlayer(
    BaseManualPlayer[TuringInfo, None, TuringGuess, TuringFeedback], TuringInGameFormatter
):
    @override
    def parse_guess(self, *, hint: None, guess_str: str) -> TuringGuess:
        code_str: str
        verifiers_str: str
        code_str, _, verifiers_str = guess_str.strip().partition(";")

        return TuringGuess(
            code=int(code_str) if code_str.isdigit() else -1,
            verifiers=[]
            if verifiers_str == ""
            else [
                int(verifier_str) if verifier_str.isdigit() else -1
                for verifier_str in verifiers_str.split(",")
            ],
        )

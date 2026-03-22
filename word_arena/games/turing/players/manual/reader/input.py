from collections.abc import Callable
from typing import override

from ......players.manual.reader.input import BaseInputManualReader
from ....common import TuringGuess


class TuringInputManualReader(BaseInputManualReader[TuringGuess]):
    @override
    def input_guess(self, *, turn_id: int, input_func: Callable[[str], str]) -> TuringGuess:
        code_str: str
        verifiers_str: str

        code_str, _, verifiers_str = tuple(
            s.strip()
            for s in input_func(
                f"Input code for guess {turn_id + 1}; "
                "to verify, further input `;` and the verifier indices (separated by commas): "
            )
            .strip()
            .partition(";")
        )

        return TuringGuess(
            code=int(code_str) if code_str.isdigit() else -1,
            verifiers=[]
            if verifiers_str == ""
            else [
                int(verifier_str) if verifier_str.isdigit() else -1
                for verifier_str in verifiers_str.split(",")
            ],
        )

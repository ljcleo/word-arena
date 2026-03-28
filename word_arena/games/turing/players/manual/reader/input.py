from collections.abc import Callable
from typing import override

from pydantic import BaseModel

from ......common.game.common import Trajectory
from ......players.manual.reader.input import BaseInputManualReader
from ....common import TuringFeedback, TuringGuess, TuringInfo


class TuringInputPromptConfig(BaseModel):
    code: str
    verify: str
    verifier: str
    add: str


class TuringInputManualReader(
    BaseInputManualReader[TuringInputPromptConfig, TuringInfo, TuringGuess, TuringFeedback]
):
    @override
    def input_guess(
        self,
        *,
        trajectory: Trajectory[TuringInfo, TuringGuess, TuringFeedback],
        input_func: Callable[[str], str],
    ) -> TuringGuess:
        turn_id: int = len(trajectory.turns) + 1
        code_str: str = input_func(self.prompt_config.code.format(turn_id=turn_id))
        code: int = int(code_str) if code_str.isdigit() else -1
        verifiers: list[int] = []

        if input_func(self.prompt_config.verify.format(turn_id=turn_id)).strip().lower()[0] == "y":
            for i in range(3):
                guess: str = input_func(
                    self.prompt_config.verifier.format(turn_id=turn_id, verifier_id=i + 1)
                )

                verifiers.append(int(guess) if guess.isdigit() else -1)

                if (
                    i < 2
                    and input_func(self.prompt_config.add.format(turn_id=turn_id))
                    .strip()
                    .lower()[0]
                    != "y"
                ):
                    break

        return TuringGuess(code=code, verifiers=verifiers)

from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....players.agent.prompter.base import BaseAgentPrompter, BaseAgentPrompterPromptConfig
from .....utils import join_or_na
from ...common import TuringError, TuringFeedback, TuringFinalResult, TuringGuess, TuringInfo


class TuringInfoPrompterPromptConfig(BaseModel):
    verifier: str
    max_turns: str
    unlimited: str


class TuringGuessPrompterPromptConfig(BaseModel):
    guess_detail: str
    final_guess: str
    verifying_guess: str
    verifiers: str


class TuringFeedbackPrompterPromptConfig(BaseModel):
    result: str
    accept: str
    verification_result: str
    verification_verdicts: tuple[str, str]
    final_guess_result: str
    final_guess_verdicts: tuple[str, str]
    reject: str
    reject_reason: str
    reject_messages: dict[TuringError, str]


class TuringFinalResultPrompterPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    num_questions: str
    has_final_guess: str
    final_guess_status: tuple[str, str]
    answer: str


class TuringAgentPrompterPromptConfig(BaseAgentPrompterPromptConfig):
    game_info: TuringInfoPrompterPromptConfig
    guess: TuringGuessPrompterPromptConfig
    feedback: TuringFeedbackPrompterPromptConfig
    final_result: TuringFinalResultPrompterPromptConfig


class TuringAgentPrompter(
    BaseAgentPrompter[
        TuringAgentPrompterPromptConfig, TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult
    ]
):
    GUESS_CLS = TuringGuess

    @override
    def get_guess_detail(
        self, *, trajectory: Trajectory[TuringInfo, TuringGuess, TuringFeedback]
    ) -> str:
        return self.prompt_config.guess.guess_detail

    @override
    def get_guess_example(
        self, *, trajectory: Trajectory[TuringInfo, TuringGuess, TuringFeedback]
    ) -> TuringGuess:
        return TuringGuess(code=123, verifiers=[0, 1, 2])

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[TuringInfo, TuringGuess, TuringFeedback],
        final_result: TuringFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: TuringInfo = trajectory.game_info
        prompt: TuringInfoPrompterPromptConfig = self.prompt_config.game_info

        for index, card in enumerate(game_info.verifiers):
            yield prompt.verifier.format(verifier_id=index), join_or_na(card)

        yield (
            prompt.max_turns,
            prompt.unlimited if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[TuringInfo, TuringGuess, TuringFeedback],
        turn_id: int,
        guess: TuringGuess,
        final_result: TuringFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        prompt: TuringGuessPrompterPromptConfig = self.prompt_config.guess

        if len(guess.verifiers) == 0:
            yield prompt.final_guess, str(guess.code)
        else:
            yield prompt.verifying_guess, str(guess.code)
            yield prompt.verifiers, join_or_na(map(str, guess.verifiers))

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[TuringInfo, TuringGuess, TuringFeedback],
        turn_id: int,
        guess: TuringGuess,
        feedback: TuringFeedback,
        final_result: TuringFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        prompt: TuringFeedbackPrompterPromptConfig = self.prompt_config.feedback

        if isinstance(feedback, list):
            yield prompt.result, prompt.accept

            yield (
                prompt.verification_result,
                join_or_na(map(prompt.verification_verdicts.__getitem__, feedback)),
            )
        elif isinstance(feedback, bool):
            yield prompt.result, prompt.accept
            yield prompt.final_guess_result, prompt.final_guess_verdicts[feedback]
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.reject_messages[feedback]

    @override
    def prompt_final_result(
        self,
        *,
        trajectory: Trajectory[TuringInfo, TuringGuess, TuringFeedback],
        final_result: TuringFinalResult,
    ) -> Iterator[tuple[str, str]]:
        prompt: TuringFinalResultPrompterPromptConfig = self.prompt_config.final_result
        yield prompt.result, prompt.verdicts[final_result.verdict is True]
        yield prompt.num_questions, str(final_result.num_questions)
        yield prompt.has_final_guess, prompt.final_guess_status[final_result.verdict is not None]
        yield prompt.answer, str(final_result.answer)

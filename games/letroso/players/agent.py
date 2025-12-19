from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import override

from pydantic import BaseModel

from games.letroso.common import LetrosoFeedback, LetrosoFinalResult, LetrosoInfo
from games.letroso.players.common import LetrosoIOPlayer
from llm.common import Message
from players.agent.memory import Analysis, BaseMemory, GameRecord, GameSummary, Reflection, Turn
from players.agent.player import BaseAgentPlayer


class LetrosoExperience(BaseModel):
    strategy: str

    @staticmethod
    def example() -> LetrosoExperience:
        return LetrosoExperience(strategy="Follow these rules and strategies when guessing: ...")

    @staticmethod
    def example_json() -> str:
        return LetrosoExperience.example().model_dump_json()


LETROSO_ROLE_DEF = "You are an intelligent AI with a good English vocabulary."

LETROSO_GAME_RULE = """You are playing a game where you need to find one or more secret words.

All secret words are selected from a large vocabulary that covers most of the English words,
yet their lengths may vary.

Every time, you choose a word as your next guess;
the guess should be a valid English word with no more than a specific number of letters.

If the word is accepted, you will see how it matches each secret word
through a labeling string the same length as the guessed word:

A `G` label means that the relative order of the letter at that position,
compared to other `G`-labeled letters, is the same in the secret word;
however, its absolute position in the secret word can be different.

Furthermore, if multiple `G` labels are braced in `[]` into a `G` segment,
then the corresponding letters appears together in the secret word, adjacent to each other;
letters from different `G` segments are NOT adjacent to each other in the secret word,
even if the `G` segments themselves are adjacent.

A `Y` label means that the letter at that position appears in the secret word,
but its relative order compared to `G`-labeled letters is incorrect;
a `.` label means that the letter is not in the secret word, or has appeared too many times.

A head `G` segment started by `(` instead of `[` means that the secret word starts with it,
while a `[` start means that the secret word does NOT start with this segment;
a tail `G` segment ended by `)` instead of `]` means that the secret word ends with it,
while a `]` end means that the secret word does NOT end with this segment.

If the word is rejected, you will see the reason, such as invalid format or word not in vocabulary.

A secret word is considered found if and only if the word is actually guessed in a turn,
so you will need at least as many guesses as there are secret words to find all of them.

There may be a guessing limit on the total number of guesses (including rejected ones),
and the game halts if the remaining guesses are not enough to find all secret words;
therefore, you should try your best to minimize the number of guesses."""

LETROSO_GUESS_FORMAT = (
    "Your guess should be a "
    "**single word with only lowercase letters no more than the length constraint**."
)


def format_game_info(*, game_info: LetrosoInfo) -> Iterator[str]:
    yield f"Number of secret words: {game_info.num_targets}"
    yield f"Maximum number of letters in one guess: {game_info.max_letters}"

    yield (
        "Maximum number of guesses: "
        f"{'unlimited' if game_info.max_guesses <= 0 else game_info.max_guesses}"
    )


def format_trajectory(*, trajectory: Iterable[Turn[None, str, LetrosoFeedback]]) -> Iterator[str]:
    yield "Guess History"
    sections: list[str] = []

    for index, turn in enumerate(trajectory):
        sections.extend(
            (f"Guess {index + 1}", f"Guess: {turn.guess}", f"Feedback: {turn.feedback}")
        )

    if len(sections) == 0:
        sections.append("(Empty)")

    yield "\n".join(sections)


def format_analysis(*, analysis: Analysis) -> Iterator[str]:
    yield "Analysis from the Last Guess:"
    yield str(analysis)


def format_final_result(*, final_result: LetrosoFinalResult) -> Iterator[str]:
    yield f"Found {final_result.num_found} word(s) before game halts"
    yield f"Secret Words: {'/'.join(final_result.answers)}"


class LetrosoMemory(
    BaseMemory[LetrosoInfo, None, str, LetrosoFeedback, LetrosoFinalResult, LetrosoExperience]
):
    @override
    def make_create_experience_messages(self) -> Iterator[Message]:
        yield self._make_system_message(num_trial=0)

        yield Message.human(
            "Now, initialize some notes about the possible strategies.", *self._make_note_prompt()
        )

    @override
    def make_reflection_messages(
        self, *, record: GameRecord[LetrosoInfo, None, str, LetrosoFeedback, LetrosoFinalResult]
    ) -> Iterator[Message]:
        yield self._make_system_message(num_trial=1)
        yield self._make_record_message(record=record, reflection=None)

        yield Message.human(
            "Now, reflect on your performance in the game.",
            "Make a summary of your guesses and summarize the lessons you have learned.",
            "Pay attention to the rounds where you had little information gain.",
            "Make your response clear and simple in JSON format like "
            f"`{Reflection.example_json()}`.",
        )

    @override
    def make_update_experience_messages(
        self,
        *,
        history: list[GameSummary[LetrosoInfo, None, str, LetrosoFeedback, LetrosoFinalResult]],
    ) -> Iterator[Message]:
        yield self._make_system_message(num_trial=len(self._history))

        for index, summary in enumerate(history):
            yield self._make_record_message(
                record=summary.record, reflection=summary.reflection, index=index + 1
            )

        yield Message.human(
            "Current Notes about Possible Strategies:",
            "(Empty)" if self.experience is None else self.experience.strategy,
        )

        yield Message.human(
            "Now, update your notes about the possible strategies.",
            *self._make_note_prompt(),
        )

    def _make_system_message(self, *, num_trial: int) -> Message:
        return Message.system(
            LETROSO_ROLE_DEF,
            "The following section describes a word game:",
            "\n".join(
                f"> {line}" for line in (*LETROSO_GAME_RULE.split("\n"), "", LETROSO_GUESS_FORMAT)
            ),
            (
                "Now, you are new to the game and have no trials yet."
                if num_trial == 0
                else "Now, you have played this game once."
                if num_trial == 1
                else f'Now, you have played this game {num_trial} times".'
            ),
        )

    def _make_record_message(
        self,
        *,
        record: GameRecord[LetrosoInfo, None, str, LetrosoFeedback, LetrosoFinalResult],
        reflection: Reflection | None,
        index: int | None = None,
    ) -> Message:
        sections: list[str] = []
        if index is not None:
            sections.append(f"Trial {index}")

        sections.extend(
            (
                *format_game_info(game_info=record.game_info),
                *format_trajectory(trajectory=record.trajectory),
            )
        )

        if record.latest_analysis is not None:
            sections.extend(format_analysis(analysis=record.latest_analysis))

        sections.extend(format_final_result(final_result=record.final_result))
        if reflection is not None:
            sections.extend(("Your reflection:", reflection.model_dump_json()))

        return Message.human(*sections)

    def _make_note_prompt(self) -> Iterator[str]:
        yield "The notes should help you make a good guess in a turn."

        yield (
            "Make your response clear and simple in JSON format like "
            f"`{LetrosoExperience.example_json()}`."
        )


class LetrosoAgentPlayer(
    BaseAgentPlayer[LetrosoInfo, None, str, LetrosoFeedback, LetrosoFinalResult, LetrosoExperience],
    LetrosoIOPlayer,
):
    @override
    def make_guess_info_messages(
        self,
        *,
        game_info: LetrosoInfo,
        experience: LetrosoExperience,
        current_trajectory: Iterable[Turn[None, str, LetrosoFeedback]],
        latest_analysis: Analysis | None,
        hint: None,
    ) -> Iterator[Message]:
        yield Message.system(
            LETROSO_ROLE_DEF,
            LETROSO_GAME_RULE,
            "Here are some notes you have made:",
            experience.strategy,
        )

        yield Message.human(*format_game_info(game_info=game_info))
        yield Message.human(*format_trajectory(trajectory=current_trajectory))

        if latest_analysis is not None:
            yield Message.human(*format_analysis(analysis=latest_analysis))

    @override
    def make_full_guess_prompt(
        self, *, hint: None, make_example: Callable[[str], str]
    ) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Understand the game rules, then plan and make your first guess."
        else:
            yield (
                "Summarize your past analysis and plans before this turn, "
                "update your knowledge about the secret word, then plan and make your next guess."
            )

        yield from self._make_guess_detail_prompt()
        yield self._make_example(make_example=make_example)

    @override
    def make_summarize_analysis_prompt(self) -> Iterator[str]:
        yield "Write a paragraph to summarize your past analysis and plans before this turn."

    @override
    def make_analyze_prompt(self) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Write a paragraph to understand the game rules."
        else:
            yield "Write a paragraph to update your knowledge about the secret word(s)."

    @override
    def make_plan_prompt(self) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Write a paragraph to plan the first guess."
        else:
            yield "Write a paragraph to plan the next guess."

        yield from self._make_guess_detail_prompt()

    @override
    def make_simple_guess_prompt(
        self, *, hint: None, make_example: Callable[[str], str]
    ) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Make your first guess."
        else:
            yield "Make your next guess."

        yield from self._make_guess_detail_prompt()
        yield self._make_example(make_example=make_example)

    def _make_guess_detail_prompt(self) -> Iterator[str]:
        yield LETROSO_GUESS_FORMAT
        yield "Pay attention to the number of remaining guesses."

    def _make_example(self, *, make_example: Callable[[str], str]) -> str:
        return f"Respond in JSON format like `{make_example('word')}`."

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import override

from pydantic import BaseModel

from games.wordle.common import WordleInfo, WordleResult
from games.wordle.players.common import WordleIOPlayer
from llm.common import Message
from players.agent.memory import Analysis, BaseMemory, GameRecord, GameSummary, Reflection, Turn
from players.agent.player import BaseAgentPlayer


class WordleExperience(BaseModel):
    strategy: str

    @staticmethod
    def example() -> WordleExperience:
        return WordleExperience(strategy="Follow these rules and strategies when guessing: ...")

    @staticmethod
    def example_json() -> str:
        return WordleExperience.example().model_dump_json()


WORDLE_GAME_RULE = """You are playing a game where you need to find one or more secret words.

All secret words have 5 letters, and are selected from a large vocabulary that
covers most of the 5-letter English words.

Every time, you choose a 5-letter word as your next guess; the guess should be a valid English word.

If the word is accepted, you will see how it matches each secret word through a length-5 string:
for each position, a `G` means that the letter at that position is correct,
a `Y` means that the letter at that position should be at somewhere else,
and a `.` means that the letter is not in the secret word, or has appeared too many times;
otherwise, you will see the reject reason, such as invalid format or word not in vocabulary.

Your guess must be a **single word with 5 lowercase letters**.

A secret word is considered found if and only if the word is actually guessed in a turn,
so you will need at least as many guesses as there are secret words to find all of them.

There may be a guessing limit on the total number of guesses (including rejected ones),
and the game halts if the remaining guesses are not enough to find all secret words;
therefore, you should try your best to minimize the number of guesses."""


def format_game_info(*, game_info: WordleInfo) -> Iterator[str]:
    yield f"Number of secret words: {game_info.num_targets}"

    yield (
        "Maximum number of guesses: "
        f"{'unlimited' if game_info.max_guesses <= 0 else game_info.max_guesses}"
    )


def format_trajectory(*, trajectory: Iterable[Turn[None, str, WordleResult]]) -> Iterator[str]:
    yield "Guess History"
    sections: list[str] = []

    for index, turn in enumerate(trajectory):
        sections.extend((f"Guess {index + 1}", f"Guess: {turn.guess}", f"Result: {turn.result}"))
    if len(sections) == 0:
        sections.append("(Empty)")

    yield "\n".join(sections)


def format_analysis(*, analysis: Analysis) -> Iterator[str]:
    yield "Analysis from the Last Guess:"
    yield str(analysis)


class WordleMemory(BaseMemory[WordleInfo, None, str, WordleResult, list[str], WordleExperience]):
    @override
    def make_create_experience_messages(self) -> Iterator[Message]:
        yield self._make_system_message(num_trial=0)

        yield Message.human(
            "Now, initialize some notes about the possible strategies.", *self._make_note_prompt()
        )

    @override
    def make_reflection_messages(
        self, *, record: GameRecord[WordleInfo, None, str, WordleResult, list[str]]
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
        history: list[GameSummary[WordleInfo, None, str, WordleResult, list[str]]],
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
        rule_hint: str = "\n".join(f"> {line}" for line in WORDLE_GAME_RULE.split("\n"))
        trial_hint: str

        if num_trial == 0:
            trial_hint = "Now, you are new to the game and have no trials yet."
        elif num_trial == 1:
            trial_hint = "Now, you have played this game once."
        else:
            trial_hint = f'Now, you have played this game {num_trial} times".'

        return Message.system(
            "You are an intelligent AI with a good English vocabulary.\n\n"
            "The following section describes a word guessing game:\n\n"
            f"{rule_hint}\n\n{trial_hint}"
        )

    def _make_record_message(
        self,
        *,
        record: GameRecord[WordleInfo, None, str, WordleResult, list[str]],
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

        sections.append(f"Secret Words: {'/'.join(record.final_result)}")
        if reflection is not None:
            sections.extend(("Your reflection:", reflection.model_dump_json()))

        return Message.human(*sections)

    def _make_note_prompt(self) -> Iterator[str]:
        yield "The notes should help you guess a good word in a turn."

        yield (
            "Make your response clear and simple in JSON format like "
            f"`{WordleExperience.example_json()}`."
        )


class WordleAgentPlayer(
    BaseAgentPlayer[WordleInfo, None, str, WordleResult, list[str], WordleExperience],
    WordleIOPlayer,
):
    @override
    def make_guess_info_messages(
        self,
        *,
        game_info: WordleInfo,
        experience: WordleExperience,
        current_trajectory: Iterable[Turn[None, str, WordleResult]],
        latest_analysis: Analysis | None,
        hint: None,
    ) -> Iterator[Message]:
        yield Message.system(
            "\n---\n".join(
                [
                    "You are an intelligent AI good at understanding word relations.\n\n"
                    f"{WORDLE_GAME_RULE}",
                    experience.strategy,
                ]
            )
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
        yield f"Respond in JSON format like `{make_example('word')}`."

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
        yield f"Respond in JSON format like `{make_example('word')}`."

    def _make_guess_detail_prompt(self) -> Iterator[str]:
        yield "Your guess should be a **single word with 5 lowercase letters**."
        yield "Pay attention to the number of remaining guesses."

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import override

from pydantic import BaseModel

from games.contexto.common import ContextoFeedback, ContextoFinalResult
from games.contexto.players.common import ContextoIOPlayer
from llm.common import Message
from players.agent.memory import Analysis, BaseMemory, GameRecord, GameSummary, Reflection, Turn
from players.agent.player import BaseAgentPlayer


class ContextoExperience(BaseModel):
    law: str
    strategy: str

    @staticmethod
    def example() -> ContextoExperience:
        return ContextoExperience(
            law="...", strategy="Follow these rules and strategies when guessing: ..."
        )

    @staticmethod
    def example_json() -> str:
        return ContextoExperience.example().model_dump_json()


CONTEXTO_GAME_RULE = """You are playing a game where you need to find a secret word.

The game holds a word list with tens of thousands words, including the secret word,
sorted by the similarity to the secret word.

The position of the secret word is 1; the position of the word closest to the secret word
(but not the secret word itself) is 2; the position of the furthest word is 500.

Word similarity is based on the context in which words are used on the internet,
related to both meaning and proximity.

Every time, you choose a word as your next guess; the word will be lemmatized to its stem form.

If the word is accepted, you will see its lemma and the lemma's position in the list,
otherwise you will see the reject reason, such as invalid format, word not in list, or taboo words.

Your guess must be a **single word with only lowercase letters and no hyphens**.

You should try your best to minimize the number of guesses; there may be a guessing limit."""


def format_game_info(*, game_info: int) -> Iterator[str]:
    yield f"Maximum number of guesses: {'unlimited' if game_info <= 0 else game_info}"


def format_trajectory(*, trajectory: Iterable[Turn[None, str, ContextoFeedback]]) -> Iterator[str]:
    yield "Guess History:"
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


def format_final_result(*, final_result: ContextoFinalResult) -> Iterator[str]:
    yield f"Best Guess Position: {final_result.best_pos + 1}"
    yield f"Secret Word: {final_result.top_words[0]}"
    yield f"Top 30 Words: {', '.join(final_result.top_words[:30])}"


class ContextoMemory(
    BaseMemory[int, None, str, ContextoFeedback, ContextoFinalResult, ContextoExperience]
):
    @override
    def make_create_experience_messages(self) -> Iterator[Message]:
        yield self._make_system_message(num_trial=0)

        yield Message.human(
            "Now, initialize some notes about the word similarity laws and possible strategies.",
            *self._make_note_prompt(),
        )

    @override
    def make_reflection_messages(
        self, *, record: GameRecord[int, None, str, ContextoFeedback, ContextoFinalResult]
    ) -> Iterator[Message]:
        yield self._make_system_message(num_trial=1)
        yield self._make_record_message(record=record, reflection=None)

        yield Message.human(
            "Now, reflect on your performance in the game.",
            "Make a summary of your guesses and summarize the lessons you have learned.",
            "Pay attention to the rounds where you guessed very close or very far words.",
            "Make your response clear and simple in JSON format like "
            f"`{Reflection.example_json()}`.",
        )

    @override
    def make_update_experience_messages(
        self, *, history: list[GameSummary[int, None, str, ContextoFeedback, ContextoFinalResult]]
    ) -> Iterator[Message]:
        yield self._make_system_message(num_trial=len(self._history))

        for index, summary in enumerate(history):
            yield self._make_record_message(
                record=summary.record, reflection=summary.reflection, index=index + 1
            )

        yield Message.human(
            "Current Notes about Word Similarity Laws:",
            "(Empty)" if self.experience is None else self.experience.law,
        )

        yield Message.human(
            "Current Notes about Possible Strategies:",
            "(Empty)" if self.experience is None else self.experience.strategy,
        )

        yield Message.human(
            "Now, update your notes about the word similarity laws and possible strategies.",
            *self._make_note_prompt(),
        )

    def _make_system_message(self, *, num_trial: int) -> Message:
        rule_hint: str = "\n".join(f"> {line}" for line in CONTEXTO_GAME_RULE.split("\n"))
        trial_hint: str

        if num_trial == 0:
            trial_hint = "Now, you are new to the game and have no trials yet."
        elif num_trial == 1:
            trial_hint = "Now, you have played this game once."
        else:
            trial_hint = f'Now, you have played this game {num_trial} times".'

        return Message.system(
            "You are an intelligent AI good at understanding word relations.\n\n"
            "The following section describes a word relation game:\n\n"
            f"{rule_hint}\n\n{trial_hint}"
        )

    def _make_record_message(
        self,
        *,
        record: GameRecord[int, None, str, ContextoFeedback, ContextoFinalResult],
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
        yield "The notes should help you guess a good word in a turn."

        yield (
            "Make your response clear and simple in JSON format like "
            f"`{ContextoExperience.example_json()}`."
        )


class ContextoAgentPlayer(
    BaseAgentPlayer[int, None, str, ContextoFeedback, ContextoFinalResult, ContextoExperience],
    ContextoIOPlayer,
):
    @override
    def make_guess_info_messages(
        self,
        *,
        game_info: int,
        experience: ContextoExperience,
        current_trajectory: Iterable[Turn[None, str, ContextoFeedback]],
        latest_analysis: Analysis | None,
        hint: None,
    ) -> Iterator[Message]:
        yield Message.system(
            "\n---\n".join(
                [
                    "You are an intelligent AI good at understanding word relations.\n\n"
                    f"{CONTEXTO_GAME_RULE}",
                    f"{experience.law}\n\n{experience.strategy}",
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
            yield "Write a paragraph to update your knowledge about the secret word."

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
        yield "Your guess should be a **single word with only lowercase letters and no hyphens**."
        yield "Pay attention to the number of remaining guesses."

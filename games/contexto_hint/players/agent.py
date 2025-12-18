from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import override

from pydantic import BaseModel

from games.contexto_hint.players.common import (
    ContextoHintIOPlayer,
    index_to_option,
    make_option,
    make_options,
)
from llm.common import Message
from players.agent.memory import Analysis, BaseMemory, GameRecord, GameSummary, Reflection, Turn
from players.agent.player import BaseAgentPlayer


class ContextoHintExperience(BaseModel):
    law: str
    strategy: str

    @staticmethod
    def example() -> ContextoHintExperience:
        return ContextoHintExperience(
            law="...", strategy="Follow these rules and strategies when guessing: ..."
        )

    @staticmethod
    def example_json() -> str:
        return ContextoHintExperience.example().model_dump_json()


CONTEXTO_HINT_GAME_RULE: str = """You are playing a game where you need to find a secret word.

The game holds a word list with 500 words, including the secret word,
sorted by the similarity to the secret word.

The position of the secret word is 1; the position of the word closest to the secret word
(but not the secret word itself) is 2; the position of the furthest word is 500.

Word similarity is based on the context in which words are used on the internet,
related to both meaning and proximity.

Every time, the game provides several candidate words from the list that
you have not guessed before, but without their positions.

You need to choose one of them as your next guess, then you will see its position in the list.

It is guaranteed that there is a candidate word closer than the current best guess."""


def format_trajectory(
    *, trajectory: Iterable[Turn[list[str], int, int]], final_result: list[str] | None
) -> Iterator[str]:
    yield "Guess History:"
    sections: list[str] = []

    word_pos: dict[str, int] | None = (
        None if final_result is None else {word: pos + 1 for pos, word in enumerate(final_result)}
    )

    for index, turn in enumerate(trajectory):
        candidates: str = (
            ", ".join(turn.hint)
            if word_pos is None
            else ", ".join(f"{word} (Position: {word_pos[word]})" for word in turn.hint)
        )

        sections.extend((f"Guess {index + 1}", f"Candidates: {candidates}"))

        if turn.result == -1:
            sections.append("Got Invalid Guess Input")
        else:
            sections.extend((f"Guess: {turn.hint[turn.guess]}", f"Position: {turn.result + 1}"))

    if len(sections) == 0:
        sections.append("(Empty)")

    yield "\n".join(sections)


def format_analysis(*, analysis: Analysis) -> Iterator[str]:
    yield "Analysis from the Last Guess:"
    yield str(analysis)


class ContextoHintMemory(BaseMemory[None, list[str], int, int, list[str], ContextoHintExperience]):
    @override
    def make_create_experience_messages(self) -> Iterator[Message]:
        yield self._make_system_message(num_trial=0)

        yield Message.human(
            "Now, initialize some notes about the word similarity laws and possible strategies.",
            *self._make_note_prompt(),
        )

    @override
    def make_reflection_messages(
        self, *, record: GameRecord[None, list[str], int, int, list[str]]
    ) -> Iterator[Message]:
        yield self._make_system_message(num_trial=1)
        yield self._make_record_message(record=record, reflection=None)

        yield Message.human(
            "Now, reflect on your performance in the game.",
            "Make a summary of your guesses and summarize the lessons you have learned.",
            "Pay attention to the rounds where you failed to choose the word "
            "with the closest position among the candidates.",
            "Make your response clear and simple in JSON format like "
            f"`{Reflection.example_json()}`.",
        )

    @override
    def make_update_experience_messages(
        self, *, history: list[GameSummary[None, list[str], int, int, list[str]]]
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
        rule_hint: str = "\n".join(f"> {line}" for line in CONTEXTO_HINT_GAME_RULE.split("\n"))
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
        record: GameRecord[None, list[str], int, int, list[str]],
        reflection: Reflection | None,
        index: int | None = None,
    ) -> Message:
        sections: list[str] = []
        if index is not None:
            sections.append(f"Trial {index}")

        sections.extend(
            format_trajectory(trajectory=record.trajectory, final_result=record.final_result)
        )
        if record.latest_analysis is not None:
            sections.extend(format_analysis(analysis=record.latest_analysis))

        sections.extend(
            (
                f"Secret Word: {record.final_result[0]}",
                f"Top 30 Words: {', '.join(record.final_result[:30])}",
            )
        )

        if reflection is not None:
            sections.extend(("Your Reflection:", reflection.model_dump_json()))

        return Message.human(*sections)

    def _make_note_prompt(self) -> Iterator[str]:
        yield "The notes should help you choose the best word among the candidates."

        yield (
            "Make your response clear and simple in JSON format like "
            f"`{ContextoHintExperience.example_json()}`."
        )


class ContextoHintAgentPlayer(
    BaseAgentPlayer[None, list[str], int, int, list[str], ContextoHintExperience],
    ContextoHintIOPlayer,
):
    @override
    def make_guess_info_messages(
        self,
        *,
        game_info: None,
        experience: ContextoHintExperience,
        current_trajectory: Iterable[Turn[list[str], int, int]],
        latest_analysis: Analysis | None,
        hint: list[str],
    ) -> Iterator[Message]:
        yield Message.system(
            "\n---\n".join(
                [
                    "You are an intelligent AI good at understanding word relations.\n\n"
                    f"{CONTEXTO_HINT_GAME_RULE}",
                    f"{experience.law}\n\n{experience.strategy}",
                ]
            )
        )

        yield Message.human(*format_trajectory(trajectory=current_trajectory, final_result=None))
        if latest_analysis is not None:
            yield Message.human(*format_analysis(analysis=latest_analysis))

        yield Message.human("Candidates of the Next Guess:", make_options(hint=hint))

    @override
    def make_full_guess_prompt(
        self, *, hint: list[str], make_example: Callable[[str], str]
    ) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Understand the game rules, plan for your next guess and make your choice."
        else:
            yield (
                "Summarize your past analysis and plans before this turn, "
                "update your knowledge about the secret word, "
                "plan your next guess and make your choice."
            )

        yield from self._make_guess_detail_prompt(hint=hint)
        yield f"Respond in JSON format like `{make_example('B')}`."

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
        yield "Write a paragraph to plan your next guess."

    @override
    def make_simple_guess_prompt(
        self, *, hint: list[str], make_example: Callable[[str], str]
    ) -> Iterator[str]:
        yield "Make your choice."
        yield from self._make_guess_detail_prompt(hint=hint)
        yield f"Respond in JSON format like `{make_example('B')}`."

    def _make_guess_detail_prompt(self, *, hint: list[str]) -> Iterator[str]:
        example_id: int = 1
        yield "You should reply the OPTION CHARACTER of the guessed word, NOT the word itself."

        yield (
            f"For example, reply `{index_to_option(example_id)}` "
            f"if you choose `{make_option(example_id, hint[example_id])}`."
        )

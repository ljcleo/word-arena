from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import override

from pydantic import BaseModel

from games.contexto.common import ContextoError, ContextoResult
from llm.common import Message
from players.agent.memory import Analysis, BaseMemory, GameRecord, Reflection, Turn
from players.agent.player import BaseAgentPlayer


class ContextoExperience(BaseModel):
    law: str
    strategy: str

    @staticmethod
    def example() -> ContextoExperience:
        return ContextoExperience(
            law="In summary, the word similarity obeys these laws: ...",
            strategy="Follow these rules and strategies when guessing: ...",
        )

    @staticmethod
    def example_str() -> str:
        return ContextoExperience.example().model_dump_json()


def make_game_rule(*, max_guesses: int) -> str:
    return f"""You are playing a game where you need to find a secret word.

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

You have {"unlimited" if max_guesses <= 0 else max_guesses} guesses in total."""


def process_trajectory(*, trajectory: Iterable[Turn[None, str, ContextoResult]]) -> str:
    sections: list[str] = []
    index: int = -1

    for index, turn in enumerate(trajectory):
        analysis: Analysis | None = turn["analysis"]
        guess: str = turn["guess"]
        result: ContextoResult = turn["result"]
        result_str: str

        if isinstance(result, ContextoError):
            result_str = f"Reject -- {result.error}"
        else:
            result_str = f"Accept -- Lemmatized as {result.lemma}; Position {result.distance + 1}"

        if analysis is not None:
            sections.extend(
                (
                    f"Analysis Before Guess {index + 1}: {analysis.analysis}",
                    f"Plan Before Guess {index + 1}: {analysis.plan}",
                )
            )

        sections.extend(
            (
                f"Guess {index + 1}",
                f"Guess: {guess}",
                f"Result: {result_str}",
            )
        )

    if index == -1:
        sections.append("(empty)")

    return "\n".join(sections)


class ContextoMemory(BaseMemory[int, None, str, ContextoResult, list[str], ContextoExperience]):
    @override
    def process_game_info(self, *, game_info: int) -> None:
        pass

    @override
    def make_create_experience_messages(self) -> Iterator[Message]:
        yield self._make_system_message(max_guesses=self.game_info, num_trial=0)

        yield Message.human(
            "Now, initialize some notes about the word similarity laws and possible strategies.",
            *self._make_note_prompt(),
        )

    @override
    def make_reflection_messages(
        self,
        *,
        game_info: int,
        trajectory: Iterable[Turn[None, str, ContextoResult]],
        summary: list[str],
    ) -> Iterator[Message]:
        assert game_info == self.game_info
        yield self._make_system_message(max_guesses=self.game_info, num_trial=1)
        yield self._make_record_message(trajectory=trajectory, summary=summary, reflection=None)

        yield Message.human(
            "Now, reflect on your performance in the game.",
            "Make a summary of your guesses and summarize the lessons you have learned.",
            "Pay attention to the rounds where you guessed very close or very far words.",
            f"Make your response clear and simple in JSON format like `{Reflection.example()}`.",
        )

    @override
    def make_update_experience_messages(
        self, *, history: list[GameRecord[int, None, str, ContextoResult, list[str]]]
    ) -> Iterator[Message]:
        for record in history:
            assert record["game_info"] == self.game_info

        yield self._make_system_message(max_guesses=self.game_info, num_trial=len(self._history))

        for index, record in enumerate(history):
            yield self._make_record_message(
                trajectory=record["trajectory"],
                summary=record["summary"],
                reflection=record["reflection"],
                index=index + 1,
            )

        yield Message.human(
            "Current Notes about Word Similarity Laws:",
            "(no notes yet)" if self.experience is None else self.experience.law,
        )

        yield Message.human(
            "Current Notes about Possible Strategies:",
            "(no notes yet)" if self.experience is None else self.experience.strategy,
        )

        yield Message.human(
            "Now, update your notes about the word similarity laws and possible strategies.",
            *self._make_note_prompt(),
        )

    def _make_system_message(self, *, max_guesses: int, num_trial: int) -> Message:
        rule_hint: str = "\n".join(
            f"> {line}" for line in make_game_rule(max_guesses=max_guesses).split("\n")
        )

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
        trajectory: Iterable[Turn[None, str, ContextoResult]],
        summary: list[str],
        reflection: Reflection | None,
        index: int | None = None,
    ) -> Message:
        sections: list[str] = []
        if index is not None:
            sections.append(f"Trial {index}")

        sections.extend(
            (
                "Your guess records:",
                process_trajectory(trajectory=trajectory),
                f"Secret word: {summary[0]}",
                "Top 30 words:",
                ", ".join(summary[:30]),
            )
        )

        if reflection is not None:
            sections.extend(("Your reflection:", reflection.model_dump_json()))

        return Message.human(*sections)

    def _make_note_prompt(self) -> Iterator[str]:
        yield "The notes should help you guess a good word in a turn."

        yield (
            "Make your response clear and simple in JSON format like "
            f"`{ContextoExperience.example_str()}`."
        )


class ContextoAgentPlayer(
    BaseAgentPlayer[int, None, str, ContextoResult, list[str], ContextoExperience]
):
    @override
    def make_guess_info_messages(
        self,
        *,
        game_info: int,
        experience: ContextoExperience,
        current_trajectory: Iterable[Turn[None, str, ContextoResult]],
        hint: None,
    ) -> Iterator[Message]:
        yield Message.system(
            "\n---\n".join(
                [
                    "You are an intelligent AI good at understanding word relations.\n\n"
                    f"{make_game_rule(max_guesses=game_info)}",
                    f"{experience.law}\n\n{experience.strategy}",
                ]
            )
        )

        yield Message.human("History:", process_trajectory(trajectory=current_trajectory))

    @override
    def make_full_guess_prompt(
        self, *, hint: None, make_example: Callable[[str], str]
    ) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Understand the game rules, then plan and make your first guess."
        else:
            yield "Update your knowledge about the secret word, then plan and make your next guess."

        yield from self._make_guess_detail_prompt()
        yield f"Respond in JSON format like `{make_example('word')}`."

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

    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> str:
        return raw_guess

    def _make_guess_detail_prompt(self) -> Iterator[str]:
        yield "Your guess should be a **single word with only lowercase letters and no hyphens**."
        yield "Pay attention to the number of remaining guesses."

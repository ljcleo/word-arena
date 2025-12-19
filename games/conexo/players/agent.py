from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import override

from pydantic import BaseModel

from games.conexo.common import ConexoFeedback, ConexoFinalResult, ConexoInfo
from games.conexo.players.common import ConexoIOPlayer, format_options
from llm.common import Message
from players.agent.memory import Analysis, BaseMemory, GameRecord, GameSummary, Reflection, Turn
from players.agent.player import BaseAgentPlayer


class ConexoExperience(BaseModel):
    law: str
    strategy: str

    @staticmethod
    def example() -> ConexoExperience:
        return ConexoExperience(
            law="...", strategy="Follow these rules and strategies when guessing: ..."
        )

    @staticmethod
    def example_json() -> str:
        return ConexoExperience.example().model_dump_json()


CONEXO_ROLE_DEF = "You are an intelligent AI good at understanding word relations."

CONEXO_GAME_RULE: str = """You are playing a game where you need to find the groups behind words.

The game holds several word groups of the same size;
each group has a common theme that shall cover all words in the group,
which can be lexical, semantic, conceptual, or even phrasal (can form phrases with the same word).

At the beginning, the game provides the group size and words from all groups,
but not the groups themselves; it is guaranteed that each word belongs to exactly one group.

Every time, you choose as many words as the group size to form a guess,
then you will see whether the guessed words belong to the same group or not;
if yes, then the group is considered found.

There may be a guessing limit on the total number of guesses (including rejected ones),
and the game halts if the remaining guesses are not enough to find all word groups;
therefore, you should try your best to minimize the number of guesses."""

CONEXO_GUESS_FORMAT = (
    "You should reply the indices of the guessed words as a string "
    "where two indices are separated by a single space, NOT the words themselves."
)


def format_game_info(*, game_info: ConexoInfo) -> Iterator[str]:
    yield "Words:"
    yield format_options(game_info.words)
    yield f"Group Size: {game_info.group_size}"

    yield (
        "Maximum number of guesses: "
        f"{'unlimited' if game_info.max_guesses <= 0 else game_info.max_guesses}"
    )


def format_trajectory(
    *, game_info: ConexoInfo, trajectory: Iterable[Turn[None, set[int], ConexoFeedback]]
) -> Iterator[str]:
    yield "Guess History"
    sections: list[str] = []

    for index, turn in enumerate(trajectory):
        guess_str: str = ", ".join(
            game_info.words[index] if 0 <= index < len(game_info.words) else "(N/A)"
            for index in turn.guess
        )

        sections.extend((f"Guess {index + 1}", f"Guess: {guess_str}", f"Feedback: {turn.feedback}"))

    if len(sections) == 0:
        sections.append("(Empty)")

    yield "\n".join(sections)


def format_analysis(*, analysis: Analysis) -> Iterator[str]:
    yield "Analysis from the Last Guess:"
    yield str(analysis)


def format_final_result(*, final_result: ConexoFinalResult) -> Iterator[str]:
    yield f"Found {final_result.num_found} Group(s)"
    yield "All Groups:"

    for group in final_result.groups:
        yield " ".join((f"- {group.theme}:", *group.words))


class ConexoMemory(
    BaseMemory[ConexoInfo, None, set[int], ConexoFeedback, ConexoFinalResult, ConexoExperience]
):
    @override
    def make_create_experience_messages(self) -> Iterator[Message]:
        yield self._make_system_message(num_trial=0)

        yield Message.human(
            "Now, initialize some notes about the word group laws and possible strategies.",
            *self._make_note_prompt(),
        )

    @override
    def make_reflection_messages(
        self, *, record: GameRecord[ConexoInfo, None, set[int], ConexoFeedback, ConexoFinalResult]
    ) -> Iterator[Message]:
        yield self._make_system_message(num_trial=1)
        yield self._make_record_message(record=record, reflection=None)

        yield Message.human(
            "Now, reflect on your performance in the game.",
            "Make a summary of your guesses and summarize the lessons you have learned.",
            "Pay attention to the rounds where you successfully found a group.",
            "Make your response clear and simple in JSON format like "
            f"`{Reflection.example_json()}`.",
        )

    @override
    def make_update_experience_messages(
        self,
        *,
        history: list[GameSummary[ConexoInfo, None, set[int], ConexoFeedback, ConexoFinalResult]],
    ) -> Iterator[Message]:
        yield self._make_system_message(num_trial=len(self._history))

        for index, summary in enumerate(history):
            yield self._make_record_message(
                record=summary.record, reflection=summary.reflection, index=index + 1
            )

        yield Message.human(
            "Current Notes about Word Group Laws:",
            "(Empty)" if self.experience is None else self.experience.law,
        )

        yield Message.human(
            "Current Notes about Possible Strategies:",
            "(Empty)" if self.experience is None else self.experience.strategy,
        )

        yield Message.human(
            "Now, update your notes about the word group laws and possible strategies.",
            *self._make_note_prompt(),
        )

    def _make_system_message(self, *, num_trial: int) -> Message:
        return Message.system(
            CONEXO_ROLE_DEF,
            "The following section describes a word game:",
            "\n".join(
                f"> {line}" for line in (*CONEXO_GAME_RULE.split("\n"), "", CONEXO_GUESS_FORMAT)
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
        record: GameRecord[ConexoInfo, None, set[int], ConexoFeedback, ConexoFinalResult],
        reflection: Reflection | None,
        index: int | None = None,
    ) -> Message:
        sections: list[str] = []
        if index is not None:
            sections.append(f"Trial {index}")

        sections.extend(
            (
                *format_game_info(game_info=record.game_info),
                *format_trajectory(game_info=record.game_info, trajectory=record.trajectory),
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
            f"`{ConexoExperience.example_json()}`."
        )


class ConexoAgentPlayer(
    BaseAgentPlayer[
        ConexoInfo, None, set[int], ConexoFeedback, ConexoFinalResult, ConexoExperience
    ],
    ConexoIOPlayer,
):
    @override
    def make_guess_info_messages(
        self,
        *,
        game_info: ConexoInfo,
        experience: ConexoExperience,
        current_trajectory: Iterable[Turn[None, set[int], ConexoFeedback]],
        latest_analysis: Analysis | None,
        hint: None,
    ) -> Iterator[Message]:
        yield Message.system(
            CONEXO_ROLE_DEF,
            CONEXO_GAME_RULE,
            "Here are some notes you have made:",
            experience.law,
            experience.strategy,
        )

        yield Message.human(*format_game_info(game_info=game_info))
        yield Message.human(*format_trajectory(game_info=game_info, trajectory=current_trajectory))

        if latest_analysis is not None:
            yield Message.human(*format_analysis(analysis=latest_analysis))

    @override
    def make_full_guess_prompt(
        self, *, hint: None, make_example: Callable[[str], str]
    ) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Understand the game rules, plan for your next guess and make your choice."
        else:
            yield (
                "Summarize your past analysis and plans before this turn, "
                "update your knowledge about the groups behind remaining words, "
                "then plan and make your next guess."
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
            yield (
                "Write a paragraph to update your knowledge "
                "about the groups behind remaining words."
            )

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
        yield CONEXO_GUESS_FORMAT
        example: range = range(self.memory.game_info.group_size)

        yield (
            f"For example, reply `{' '.join(map(str, example))}` if you choose these words: "
            f"`{', '.join(self.memory.game_info.words[index] for index in example)}`."
        )

        yield "Pay attention to the number of remaining guesses."

    def _make_example(self, *, make_example: Callable[[str], str]) -> str:
        return (
            "Respond in JSON format like "
            f"`{make_example(' '.join(map(str, range(self.memory.game_info.group_size))))}`."
        )

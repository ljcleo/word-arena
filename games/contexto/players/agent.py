from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel

from agent.memory import BaseMemory, GameRecord
from agent.player import BaseAgentPlayer
from common.common import GameResult
from games.contexto.common import ContextoError, ContextoResponse
from llm.common import Message


class ContextoReflection(BaseModel):
    summary: str
    lessons: str


class ContextoExperience(BaseModel):
    law: str
    strategy: str


def make_game_rule(*, max_guesses: int) -> str:
    return f"""You are playing a game where you need to find a secret word.

The game holds a word list with tens of thousands words, including the secret word,
sorted by the similarity to the secret word.

The position of the secret word is 1; the position of the word closest to the secret word
(but not the secret word itself) is 2; the position of the furthest word is 500.

Word similarity is based on the context in which words are used on the internet,
related to both meaning and proximity.

Every time, you choose a word as your next guess; if the word is accepted,
you will see its position in the list, otherwise you will see the reject reason,
such as invalid word format, word not in list, or taboo words.

Your guess must be a **single word with only lowercase letters and no hyphens**.

You have {"unlimited" if max_guesses <= 0 else max_guesses} guesses in total."""


class ContextoMemory(
    BaseMemory[
        int,
        None,
        str,
        ContextoResponse | ContextoError,
        list[str],
        ContextoReflection,
        ContextoExperience,
    ]
):
    @override
    def process_game_info(self, *, game_info: int) -> None:
        pass

    @override
    def make_reflection_messages(
        self,
        *,
        game_result: GameResult[int, None, str, ContextoResponse | ContextoError, list[str]],
    ) -> Iterator[Message]:
        yield self._make_system_message(max_guesses=game_result["game_info"], num_trial=1)
        yield self._make_record_message(record={"game_result": game_result, "reflection": None})

        yield Message.human(
            "Now, reflect on your performance in the game.",
            "Make a summary of your guesses and summarize the lessons you have learned.",
            "Pay attention to the rounds where you guessed very close or very far words.",
            "Make your response clear and simple in JSON format like "
            '`{"summary": "In this trial, ...", "lessons": "..."}`.',
        )

    @override
    def make_update_experience_messages(
        self,
        *,
        history: list[
            GameRecord[
                int, None, str, ContextoResponse | ContextoError, list[str], ContextoReflection
            ]
        ],
    ) -> Iterator[Message]:
        yield self._make_system_message(
            max_guesses=history[0]["game_result"]["game_info"], num_trial=len(self._history)
        )

        for index, record in enumerate(history):
            yield self._make_record_message(record=record, index=index + 1)

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
            "The notes should help you guess a good word in a turn.",
            "Make your response clear and simple in JSON format like "
            '`{"law": "In summary, the word similarity obeys these laws: ...", '
            '"strategy": "Follow these rules and strategies when guessing: ..."}`.',
        )

    def _make_system_message(self, *, max_guesses: int, num_trial: int) -> Message:
        return Message.system(
            f"""You are an intelligent AI good at understanding word relations.

The following section describes a word relation game:

{"\n".join(f"> {line}" for line in make_game_rule(max_guesses=max_guesses).split("\n"))}

Now, you have played this game {"once" if num_trial == 1 else f"{num_trial} times"}."""
        )

    def _make_record_message(
        self,
        *,
        record: GameRecord[
            int, None, str, ContextoResponse | ContextoError, list[str], ContextoReflection
        ],
        index: int | None = None,
    ) -> Message:
        game_result: GameResult[int, None, str, ContextoResponse | ContextoError, list[str]] = (
            record["game_result"]
        )
        summary: list[str] = game_result["summary"]
        answer: str = summary[0]
        top_words: str = ", ".join(summary[:30])
        trajectory_sections: list[str] = []

        for index, (_, guess, result) in enumerate(game_result["trajectory"]):
            result_str: str

            if isinstance(result, ContextoError):
                result_str = f"Reject -- {result.error}"
            else:
                result_str = (
                    f"Accept -- Lemmatized as {result.lemma}; Position {result.distance + 1}"
                )

            trajectory_sections.extend(
                (
                    f"Guess Round {index + 1}",
                    f"Guess: {guess}",
                    f"Result: {result_str}",
                )
            )

        sections: list[str] = []
        if index is not None:
            sections.append(f"Trial {index}")

        sections.extend(
            (
                "Your guess records:",
                "\n".join(trajectory_sections),
                f"Secret word: {answer}",
                "Top 30 words:",
                top_words,
            )
        )

        reflection: ContextoReflection | None = record["reflection"]
        if reflection is not None:
            sections.extend(("Your reflection:", reflection.model_dump_json()))

        return Message.human(*sections)


class ContextoAgentPlayer(
    BaseAgentPlayer[
        int,
        None,
        str,
        ContextoResponse | ContextoError,
        list[str],
        ContextoReflection,
        ContextoExperience,
    ]
):
    @override
    def make_guess_info_messages(
        self,
        *,
        experience: ContextoExperience | None,
        current_trajectory: Iterable[tuple[None, str, ContextoResponse | ContextoError]],
        hint: None,
    ) -> Iterator[Message]:
        system_prompt_sections: list[str] = [
            "You are an intelligent AI good at understanding word relations.\n\n"
            f"{make_game_rule(max_guesses=self.memory.game_info)}"
        ]

        if experience is not None:
            system_prompt_sections.append(f"{experience.law}\n\n{experience.strategy}")

        yield Message.system("\n---\n".join(system_prompt_sections))

        trajectory_sections: list[str] = []

        for index, (_, guess, result) in enumerate(current_trajectory):
            result_str: str

            if isinstance(result, ContextoError):
                result_str = f"Reject -- {result.error}"
            else:
                result_str = (
                    f"Accept -- Lemmatized as {result.lemma}; Position {result.distance + 1}"
                )

            trajectory_sections.extend(
                (
                    f"Guess {index + 1}",
                    f"Guess: {guess}",
                    f"Result: {result_str}",
                )
            )

        turn_index: int = len(trajectory_sections) + 1
        if turn_index == 1:
            trajectory_sections.append("(empty)")

        yield Message.human("History:", "\n".join(trajectory_sections))

    @override
    def make_full_guess_prompt(self, *, hint: None) -> Iterator[str]:
        yield "Analyze the situation, then plan and make your next guess."
        yield "Your guess should be a **single word with only lowercase letters and no hyphens**."
        yield 'Respond in JSON format like `{"analysis": "...", "plan": "...", "guess": "word"}`.'

    @override
    def make_analyze_prompt(self) -> Iterator[str]:
        yield "Write a paragraph to analyze the situation."

    @override
    def make_plan_prompt(self) -> Iterator[str]:
        yield "Write a paragraph to plan the next guess."

    @override
    def make_simple_guess_prompt(self, *, hint: None) -> Iterator[str]:
        yield "Make your next guess."
        yield "Your guess should be a **single word with only lowercase letters and no hyphens**."
        yield 'Respond in JSON format like `{"guess": "word"}`.'

    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> str:
        return raw_guess


def main() -> None:
    from time import time_ns

    from agent.player import PromptMode
    from games.contexto.game import ContextoGameManager, ContextoGameResult
    from llm.openai import OpenAILLM

    model: OpenAILLM = OpenAILLM(
        api_key="sk-PInpH3EcNkJjwzqvB1EbBdF09e9b4b12A81fF0C325D55d71",
        base_url="https://openkey.cloud/v1",
        model="gpt-5-mini",
        max_tokens=32768,
        timeout=7200,
    )

    player: ContextoAgentPlayer = ContextoAgentPlayer(
        model=model,
        memory=ContextoMemory(
            model=model,
            reflection_type=ContextoReflection,
            experience_type=ContextoExperience,
        ),
        prompt_mode=(
            PromptMode.MULTI_TURN
            if input("Multi-turn? (y/n): ")[0].lower() == "y"
            else PromptMode.DIRECT
        )
        if input("Analyze? (y/n): ")[0].lower() == "y"
        else PromptMode.SIMPLE,
    )

    game_manager: ContextoGameManager = ContextoGameManager(seed=time_ns())

    if input("Train? (y/n): ")[0].lower() == "y":
        num_train_loops: int = 3
        num_in_loop_trials: int = 3

        for _ in range(num_train_loops):
            for i in range(num_in_loop_trials):
                result: ContextoGameResult = game_manager.create_game(
                    game_id=None, max_guesses=50
                ).play(player=player)

                player.memory.reflect(
                    summary=result["summary"], update_experience=i == num_in_loop_trials - 1
                )

    result = game_manager.create_game(game_id=int(input("Input Game ID: ")), max_guesses=50).play(
        player=player
    )

    print("You Guessed", len(result["trajectory"]), "Times")
    print("Top Words:", *result["summary"][:10])
    player.memory.reflect(summary=result["summary"], update_experience=False)


if __name__ == "__main__":
    main()

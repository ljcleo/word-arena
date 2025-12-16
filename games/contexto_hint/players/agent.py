from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel

from agent.memory import GameRecord, Turn
from agent.player import AgentMemory, Analysis, BaseAgentPlayer
from llm.common import Message


class ContextoHintReflection(BaseModel):
    summary: str
    lessons: str


class ContextoHintExperience(BaseModel):
    law: str
    strategy: str


def make_game_rule(*, num_candidates: int) -> str:
    return f"""You are playing a game where you need to find a secret word.

The game holds a word list with 500 words, including the secret word,
sorted by the similarity to the secret word.

The position of the secret word is 1; the position of the word closest to the secret word
(but not the secret word itself) is 2; the position of the furthest word is 500.

Word similarity is based on the context in which words are used on the internet,
related to both meaning and proximity.

Every time, the game provides {num_candidates} candidate words from the list that
you have not guessed before, but without their positions.

You need to choose one of them as your next guess, then you will see its position in the list.

It is guaranteed that there is a candidate word closer than the current best guess."""


def process_trajectory(
    *, trajectory: Iterable[Turn[list[str], Analysis, int, int]], summary: list[str] | None
) -> tuple[str, int]:
    word_pos: dict[str, int] | None = (
        None if summary is None else {word: pos + 1 for pos, word in enumerate(summary)}
    )

    sections: list[str] = []
    index: int = -1

    for index, turn in enumerate(trajectory):
        hint: list[str] = turn["hint"]
        analysis: Analysis | None = turn["analysis"]
        guess: int = turn["guess"]
        position: int = turn["result"] + 1
        candidates: str

        if word_pos is None:
            candidates = ", ".join(hint)
        else:
            candidates = ", ".join(f"{word} (Position: {word_pos[word]})" for word in hint)

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
                f"Candidates: {candidates}",
                f"Guess: {hint[guess]}",
                f"Position: {position}",
            )
        )

    index += 2
    if index == 1:
        sections.append("(empty)")

    return "\n".join(sections), index


class ContextoHintMemory(
    AgentMemory[int, list[str], int, int, list[str], ContextoHintReflection, ContextoHintExperience]
):
    @override
    def process_game_info(self, *, game_info: int) -> None:
        pass

    @override
    def make_create_experience_messages(self) -> Iterator[Message]:
        yield self._make_system_message(num_candidates=self.game_info, num_trial=0)

        yield Message.human(
            "Now, initialize some notes about the word similarity laws and possible strategies.",
            "The notes should help you choose the best word among the candidates.",
            "Make your response clear and simple in JSON format like "
            '`{"law": "In summary, the word similarity obeys these laws: ...", '
            '"strategy": "Follow these rules and strategies when guessing: ..."}`.',
        )

    @override
    def make_reflection_messages(
        self,
        *,
        game_info: int,
        trajectory: Iterable[Turn[list[str], Analysis, int, int]],
        summary: list[str],
    ) -> Iterator[Message]:
        assert game_info == self.game_info
        yield self._make_system_message(num_candidates=self.game_info, num_trial=1)
        yield self._make_record_message(trajectory=trajectory, summary=summary, reflection=None)

        yield Message.human(
            "Now, reflect on your performance in the game.",
            "Make a summary of your guesses and summarize the lessons you have learned.",
            "Pay attention to the rounds where you failed to choose the word "
            "with the closest position among the candidates.",
            "Make your response clear and simple in JSON format like "
            '`{"summary": "In this trial, ...", "lessons": "..."}`.',
        )

    @override
    def make_update_experience_messages(
        self,
        *,
        history: list[
            GameRecord[int, list[str], Analysis, int, int, list[str], ContextoHintReflection]
        ],
    ) -> Iterator[Message]:
        for record in history:
            assert record["game_info"] == self.game_info

        yield self._make_system_message(num_candidates=self.game_info, num_trial=len(self._history))

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
            "The notes should help you choose the best word among the candidates.",
            "Make your response clear and simple in JSON format like "
            '`{"law": "In summary, the word similarity obeys these laws: ...", '
            '"strategy": "Follow these rules and strategies when guessing: ..."}`.',
        )

    def _make_system_message(self, *, num_candidates: int, num_trial: int) -> Message:
        rule_hint: str = "\n".join(
            f"> {line}" for line in make_game_rule(num_candidates=num_candidates).split("\n")
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
        trajectory: Iterable[Turn[list[str], Analysis, int, int]],
        summary: list[str],
        reflection: ContextoHintReflection | None,
        index: int | None = None,
    ) -> Message:
        sections: list[str] = []
        if index is not None:
            sections.append(f"Trial {index}")

        sections.extend(
            (
                "Your guess records:",
                process_trajectory(trajectory=trajectory, summary=summary)[0],
                f"Secret word: {summary[0]}",
                "Top 30 words:",
                ", ".join(summary[:30]),
            )
        )

        if reflection is not None:
            sections.extend(("Your reflection:", reflection.model_dump_json()))

        return Message.human(*sections)


class ContextoHintAgentPlayer(
    BaseAgentPlayer[
        int, list[str], int, int, list[str], ContextoHintReflection, ContextoHintExperience
    ]
):
    @override
    def make_guess_info_messages(
        self,
        *,
        game_info: int,
        experience: ContextoHintExperience,
        current_trajectory: Iterable[Turn[list[str], Analysis, int, int]],
        hint: list[str],
    ) -> Iterator[Message]:
        yield Message.system(
            "\n---\n".join(
                [
                    "You are an intelligent AI good at understanding word relations.\n\n"
                    f"{make_game_rule(num_candidates=game_info)}",
                    f"{experience.law}\n\n{experience.strategy}",
                ]
            )
        )

        trajectory_str: str
        turn_index: int

        trajectory_str, turn_index = process_trajectory(trajectory=current_trajectory, summary=None)

        yield Message.human("History:", trajectory_str)

        options: str = "; ".join(
            f"{chr(ord('A') + index)}: {word}" for index, word in enumerate(hint)
        )

        print("Candidates:", options)
        yield Message.human(f"Candidates of Guess {turn_index}:", options)

    @override
    def make_full_guess_prompt(self, *, hint: list[str]) -> Iterator[str]:
        yield "Analyze the situation, then plan and choose your next guess."
        yield f"For example, the choice is B if you choose {hint[1]}."
        yield 'Respond in JSON format like `{"analysis": "...", "plan": "...", "guess": "B"}`.'

    @override
    def make_analyze_prompt(self) -> Iterator[str]:
        yield "Write a paragraph to analyze the situation."

    @override
    def make_plan_prompt(self) -> Iterator[str]:
        yield "Write a paragraph to plan the next guess."

    @override
    def make_simple_guess_prompt(self, *, hint: list[str]) -> Iterator[str]:
        yield "Choose your next guess."
        yield f"For example, the choice is B if you choose {hint[1]}."
        yield 'Respond in JSON format like `{"guess": "B"}`.'

    @override
    def process_guess(self, *, hint: list[str], raw_guess: str) -> int:
        return ord(raw_guess) - ord("A")


def main() -> None:
    from pathlib import Path
    from time import time_ns

    from agent.player import PromptMode
    from games.contexto_hint.game import ContextoHintGameManager
    from llm.openai import OpenAILLM

    model: OpenAILLM = OpenAILLM(
        api_key="sk-PInpH3EcNkJjwzqvB1EbBdF09e9b4b12A81fF0C325D55d71",
        base_url="https://openkey.cloud/v1",
        model=input("LLM Model: "),
        max_tokens=32768,
        timeout=7200,
    )

    player: ContextoHintAgentPlayer = ContextoHintAgentPlayer(
        model=model,
        memory=ContextoHintMemory(
            model=model,
            reflection_type=ContextoHintReflection,
            experience_type=ContextoHintExperience,
        ),
        prompt_mode=(
            PromptMode.MULTI_TURN
            if input("Multi-turn? (y/n): ")[0].lower() == "y"
            else PromptMode.DIRECT
        )
        if input("Analyze? (y/n): ")[0].lower() == "y"
        else PromptMode.SIMPLE,
    )

    game_manager: ContextoHintGameManager = ContextoHintGameManager(
        games_dir=Path("data/contexto_hint/games"), seed=time_ns()
    )

    if input("Train? (y/n): ")[0].lower() == "y":
        num_train_loops: int = 3
        num_in_loop_trials: int = 3

        for _ in range(num_train_loops):
            for i in range(num_in_loop_trials):
                summary: list[str] = game_manager.create_game(game_id=None, num_candidates=5).play(
                    player=player
                )

                player.memory.reflect(
                    summary=summary, update_experience=i == num_in_loop_trials - 1
                )

    summary = game_manager.create_game(
        game_id=int(input("Input Game ID: ")), num_candidates=5
    ).play(player=player)

    print("You Guessed", sum(1 for _ in player.memory.current_trajectory), "Times")
    print("Top Words:", *summary[:10])
    player.memory.reflect(summary=summary, update_experience=False)


if __name__ == "__main__":
    main()

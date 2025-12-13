import enum
from typing import TypedDict, override

from pydantic import BaseModel

from common.player import BasePlayer
from llm.common import BaseLLM, Message


class Turn(TypedDict):
    index: int
    hint: list[str]
    guess: int
    result: int


class GameRecord(TypedDict):
    answer: str
    top_words: str
    trajectory: str
    reflection: str


class Memory:
    def __init__(self, model: BaseLLM) -> None:
        self._model: BaseLLM = model

        self._law: str | None = None
        self._strategy: str | None = None
        self._history: list[GameRecord] = []

    @property
    def experience(self) -> str | None:
        return (
            None
            if self._law is None or self._strategy is None
            else f"{self._law}\n\n{self._strategy}"
        )

    @property
    def history(self) -> str:
        sections: list[str] = []

        for record in self._trajectory:
            sections.extend(
                (
                    f"Guess {record['index']}",
                    f"Candidates: {', '.join(record['hint'])}",
                    f"Guess: {record['hint'][record['guess']]}",
                    f"Position: {record['result']}",
                )
            )

        return "\n".join(sections)

    def prepare(self, *, game_info: int) -> None:
        self._num_candidates: int = game_info
        self._trajectory: list[Turn] = []

    def digest(self, *, hint: list[str], guess: int, result: int) -> None:
        self._trajectory.append(
            {"index": len(self._trajectory) + 1, "hint": hint, "guess": guess, "result": result + 1}
        )

    def reflect(self, *, summary: list[str], update_experience: bool) -> None:
        answer: str = summary[0]
        top_words: str = ", ".join(summary[:30])
        word_pos: dict[str, int] = {word: pos + 1 for pos, word in enumerate(summary)}
        trajectory_sections: list[str] = []

        for record in self._trajectory:
            candidates: str = ", ".join(
                f"{word} (Position: {word_pos[word]})" for word in record["hint"]
            )

            trajectory_sections.extend(
                (
                    f"Guess Round {record['index']}",
                    f"Guess: {record['hint'][record['guess']]}",
                    f"Position: {record['result']}",
                    f"Candidates: {candidates}",
                )
            )

        trajectory: str = "\n".join(trajectory_sections)

        reflection: str = self._model.query(
            self._make_system_message(num_trial=1),
            self._make_record_message(answer=answer, top_words=top_words, trajectory=trajectory),
            Message.human(
                "Now, summarize and reflect on your performance in the game.",
                "Pay attention to the rounds where you failed to choose the word "
                "with the closest position among the candidates.",
                'Make your response a paragraph starting with "In this trial, ..."',
                "Make your response clear and simple.",
            ),
        )

        print(f"Reflection: {reflection}")

        self._history.append(
            {
                "answer": answer,
                "top_words": top_words,
                "trajectory": trajectory,
                "reflection": reflection,
            }
        )

        if update_experience:
            history_messages: list[Message] = [
                self._make_system_message(num_trial=len(self._history)),
                *(
                    self._make_record_message(
                        answer=record["answer"],
                        top_words=record["top_words"],
                        trajectory=record["trajectory"],
                        reflection=record["reflection"],
                        index=index + 1,
                    )
                    for index, record in enumerate(self._history)
                ),
            ]

            self._law = self._model.query(
                *history_messages,
                Message.human(
                    "Current Notes about Word Similarity Laws:",
                    ("(no notes yet)" if self._law is None else self._law),
                ),
                Message.human(
                    "Now, update your notes about the word similarity laws.",
                    'Start your response with "In summary, the word similarity obeys these laws:".',
                    "Make your response clear and simple.",
                ),
            )

            print("New Law:", self._law, sep="\n\n")

            self._strategy = self._model.query(
                *history_messages,
                Message.human(
                    "Current Notes about Word Similarity Laws:",
                    ("(no notes yet)" if self._law is None else self._law),
                ),
                Message.human(
                    "Current Notes about Rules/Strategies:",
                    "(no notes yet)" if self._strategy is None else self._strategy,
                ),
                Message.human(
                    "Now, update your notes about the rules/strategies to follow.",
                    "The notes should help you choose the word "
                    "with the closest position among the candidates.",
                    "You may refer to your notes about word similarity laws, "
                    "but do not repeat them.",
                    "Start your response with "
                    '"You should follow these rules and strategies when guessing:".',
                    "Make your response clear and simple.",
                ),
            )

            print("New Strategy:", self._strategy, sep="\n\n")
            self._history.clear()

    def _make_system_message(self, *, num_trial: int) -> Message:
        return Message.system(
            f"""You are an intelligent AI good at understanding word relations.

The following section describes a word relation game:

> You are playing a game where you need to find a secret word.
>
> The game holds a word list with 500 words, including the secret word, sorted by the similarity
> to the secret word.
>
> The position of the secret word is 1; the position of the word closest to the secret word
> (but not the secret word itself) is 2; the position of the furthest word is 500.
>
> Word similarity is based on the context in which words are used on the internet, related to both
> meaning and proximity.
>
> Every time, the game provides {self._num_candidates} candidate words from the list that
> you have not guessed before, but without their positions.
>
> You need to choose one of them as your next guess, then you will see its position in the list.
>
> It is guaranteed that there is a candidate word closer than the current best guess.

Now, you have played this game {"once" if num_trial == 1 else f"{num_trial} times"}.""",
        )

    def _make_record_message(
        self,
        *,
        answer: str,
        top_words: str,
        trajectory: str,
        reflection: str | None = None,
        index: int | None = None,
    ) -> Message:
        sections: list[str] = []
        if index is not None:
            sections.append(f"Trial {index}")

        sections.extend(
            (
                "Your guess records:",
                trajectory,
                f"Secret word: {answer}",
                "Top 30 words:",
                top_words,
            )
        )

        if reflection is not None:
            sections.extend(("Your reflection:", reflection))

        return Message.human(*sections)


@enum.unique
class PromptMode(enum.Enum):
    SIMPLE = enum.auto()
    DIRECT = enum.auto()
    MULTI_TURN = enum.auto()


class SimpleGuess(BaseModel):
    choice: str


class FullGuess(BaseModel):
    analysis: str
    plan: str
    choice: str


class ContextoHintAgentPlayer(BasePlayer[int, list[str], int, int]):
    def __init__(self, *, model: BaseLLM, prompt_mode: PromptMode):
        self._model: BaseLLM = model
        self._prompt_mode: PromptMode = prompt_mode
        self._memory: Memory = Memory(model=model)

    @property
    def memory(self) -> Memory:
        return self._memory

    @override
    def prepare(self, *, game_info: int) -> None:
        self._memory.prepare(game_info=game_info)
        self._num_candidates: int = game_info
        self._index: int = 0

    @override
    def guess(self, *, hint: list[str]) -> int:
        self._index += 1

        options: str = "; ".join(
            f"{chr(ord('A') + index)}: {word}" for index, word in enumerate(hint)
        )

        choice: str = "A"
        print("Candidates:", options)

        msgs: list[Message] = [
            self._make_system_message(),
            Message.human("History:", "(empty)" if self._index == 1 else self._memory.history),
            Message.human(f"Candidates of Guess {self._index}:", options),
        ]

        if self._prompt_mode == PromptMode.DIRECT:
            full_guess: FullGuess = self._model.parse(
                *msgs,
                Message.human(
                    "Analyze the situation, then plan and choose your next guess.",
                    "Respond a JSON string that strictly follows this format:",
                    '{"analysis": "...", "plan": "...", "choice": "B"}',
                    f"For example, the choice is B if you choose {hint[1]}."
                    "DO NOT add anything else.",
                ),
                format=FullGuess,
            )

            print("AI Analysis:", full_guess.analysis)
            print("AI Plan:", full_guess.plan)
            choice = full_guess.choice
        else:
            if self._prompt_mode == PromptMode.MULTI_TURN:
                msgs.append(Message.human("Write a paragraph to analyze the situation."))
                analysis: str = self._model.query(*msgs)
                print("AI Analysis:", analysis)
                msgs.append(Message.ai(analysis))

                msgs.append(Message.human("Write a paragraph to plan the next guess."))
                plan: str = self._model.query(*msgs)
                print("AI Plan:", plan)
                msgs.append(Message.ai(plan))

            choice = self._model.parse(
                *msgs,
                Message.human(
                    "Choose your next guess.",
                    "Respond a JSON string that strictly follows this format:",
                    '{"choice": "B"}',
                    f"For example, the choice is B if you choose {hint[1]}."
                    "DO NOT add anything else.",
                ),
                format=SimpleGuess,
            ).choice

        print("AI Choice:", choice)
        guess: int = ord(choice) - ord("A")
        print("AI Guess:", hint[guess])
        return guess

    @override
    def digest(self, *, hint: list[str], guess: int, result: int) -> None:
        print("Position:", result + 1)
        self._memory.digest(hint=hint, guess=guess, result=result)

    def _make_system_message(self) -> Message:
        sections: list[str] = [
            f"""You are an intelligent AI good at understanding word relations.

You are playing a game where you need to find a secret word.

The game holds a word list with 500 words, including the secret word, sorted by the similarity
to the secret word.

The position of the secret word is 1; the position of the word closest to the secret word
(but not the secret word itself) is 2; the position of the furthest word is 500.

Word similarity is based on the context in which words are used on the internet, related to both
meaning and proximity.

Every time, the game provides {self._num_candidates} candidate words from the list that you have not
guessed before, but without their positions.

You need to choose one of them as your next guess, then you will see its position in the list.

It is guaranteed that there is a candidate word closer than the current best guess."""
        ]

        experience: str | None = self._memory.experience
        if experience is not None:
            sections.append(experience)

        return Message.system("\n---\n".join(sections))

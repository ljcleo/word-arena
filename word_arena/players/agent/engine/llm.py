from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from itertools import chain
from typing import override

from pydantic import BaseModel, create_model

from ....common.game.common import Trajectory
from ....common.llm.common import Message
from ....common.llm.llm import LLM
from ..common import Analysis, AnalyzedGuess, GameRecord, GameSummary, Reflection
from ..state import AgentGameStateInterface, AgentNoteStateInterface
from .base import BaseAgentEngine


def maybe_to_xml(*, key: str, values: str | Iterable[str]) -> Iterator[str]:
    key = key.lower().replace(" ", "_")
    if isinstance(values, str):
        values = (values,)

    def iter_with_key() -> Iterator[str]:
        flag: bool = False

        for value in values:
            if not flag:
                yield f"<{key}>"
                flag = True

            yield value

        if flag:
            yield f"</{key}>"

    result: str = "".join(iter_with_key())
    if result != "":
        yield result


def leaves_to_xmls(*, items: Iterable[tuple[str, str]]) -> Iterator[str]:
    for key, value in items:
        yield from maybe_to_xml(key=key, values=value)


def two_layer_to_xml(*, key: str, items: Iterable[tuple[str, str]]) -> Iterator[str]:
    yield from maybe_to_xml(key=key, values=leaves_to_xmls(items=items))


def make_json_prompt(*, example: BaseModel) -> str:
    return f"Respond in JSON format like `{example.model_dump_json()}`."


def maybe_iter_with_title(*, title: str, sections: Iterable[str]) -> Iterator[str]:
    flag: bool = False

    for section in sections:
        if not flag:
            yield title
            flag = True

        yield section


class BaseLLMAgentEngine[IT, GT: BaseModel, FT, RT, NT: BaseModel](
    BaseAgentEngine[IT, GT, FT, RT, NT], ABC
):
    ROLE_DEFINITION: str
    GAME_RULE: str
    NOTE_CLS: type[NT]
    NOTE_EXAMPLE: NT
    GUESS_CLS: type[GT]

    def __init__(self, *, model: LLM, do_analyze: bool):
        self._model: LLM = model
        self._do_analyze: bool = do_analyze

    @override
    def create_note(self) -> NT:
        return self._model.query(
            Message.human(
                "# Instruction",
                "Initialize some notes that help you make a good guess in a turn.",
                *self._make_note_format_prompt(),
            ),
            format=self.NOTE_CLS,
            system_instruction=self._make_reflect_system_instruction(
                status="You have not played the game yet."
            ),
        )

    @override
    def analyze_and_guess(
        self,
        *,
        note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT],
        game_state: AgentGameStateInterface[IT, GT, FT, RT],
    ) -> AnalyzedGuess[GT]:
        system_instruction: str = self._make_guess_system_instruction(note_state=note_state)
        messages: list[Message] = [
            Message.human(*self._make_guess_prompt(game_state=game_state)),
        ]

        analysis: Analysis | None = None
        guess: GT

        if self._do_analyze:
            full_guess: BaseModel = self._model.query(
                *messages,
                format=create_model("Guess", analysis=Analysis, guess=self.GUESS_CLS),
                system_instruction=system_instruction,
            )

            analysis = getattr(full_guess, "analysis")
            guess = getattr(full_guess, "guess")
            assert analysis is not None
        else:
            guess = self._model.query(
                *messages, format=self.GUESS_CLS, system_instruction=system_instruction
            )

        return AnalyzedGuess(analysis=analysis, guess=guess)

    @override
    def summarize_and_reflect(
        self,
        *,
        note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT],
        game_state: AgentGameStateInterface[IT, GT, FT, RT],
    ) -> GameSummary[IT, GT, FT, RT]:
        reflection: Reflection = self._model.query(
            Message.human(
                *maybe_iter_with_title(
                    title="# Current Notes",
                    sections=leaves_to_xmls(items=self._prompt_note(note_state=note_state)),
                ),
                *maybe_iter_with_title(
                    title="# Game Record",
                    sections=self._make_game_record_prompt(game_record=game_state.game_record),
                ),
                "# Instruction",
                "Make a summary of the game process, then reflect on your performance.",
                *self._make_reflection_format_prompt(),
            ),
            format=Reflection,
            system_instruction=self._make_reflect_system_instruction(
                status="You have played the game once."
            ),
        )

        return GameSummary(game_record=game_state.game_record, reflection=reflection)

    @override
    def update_note(self, *, note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT]) -> NT:
        return self._model.query(
            Message.human(
                *maybe_iter_with_title(
                    title="# Current Notes",
                    sections=leaves_to_xmls(items=self._prompt_note(note_state=note_state)),
                ),
                *maybe_iter_with_title(
                    title="# Trials", sections=self._make_history_prompt(note_state=note_state)
                ),
                "# Instruction",
                "Create some improved notes based on what you have learned from your trials.",
                *self._make_note_format_prompt(),
            ),
            format=self.NOTE_CLS,
            system_instruction=self._make_reflect_system_instruction(
                status="You have played the game a few times."
            ),
        )

    @abstractmethod
    def make_note_detail_prompt(self) -> Iterator[str]: ...

    @abstractmethod
    def make_guess_detail_prompt(
        self, *, game_state: AgentGameStateInterface[IT, GT, FT, RT]
    ) -> Iterator[str]: ...

    @abstractmethod
    def make_reflect_detail_prompt(self) -> Iterator[str]: ...

    @abstractmethod
    def get_guess_example(self, *, game_state: AgentGameStateInterface[IT, GT, FT, RT]) -> GT: ...

    @abstractmethod
    def prompt_game_info(
        self, *, trajectory: Trajectory[IT, GT, FT], final_result: RT | None
    ) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[IT, GT, FT],
        turn_id: int,
        guess: GT,
        final_result: RT | None,
    ) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[IT, GT, FT],
        turn_id: int,
        guess: GT,
        feedback: FT,
        final_result: RT | None,
    ) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def prompt_final_result(
        self, *, game_record: GameRecord[IT, GT, FT, RT]
    ) -> Iterator[tuple[str, str]]: ...

    def _make_reflect_system_instruction(self, *, status: str) -> str:
        return "\n\n".join(
            (
                *maybe_iter_with_title(title="# Identity", sections=self._make_role_def_prompt()),
                *maybe_iter_with_title(title="# Game Rule", sections=self._make_game_rule_prompt()),
                "# Current Status",
                status,
            )
        )

    def _make_note_format_prompt(self) -> Iterator[str]:
        yield from self.make_note_detail_prompt()
        yield "Make your response clear and concise."
        yield make_json_prompt(example=self.NOTE_EXAMPLE)

    def _make_guess_system_instruction(
        self, *, note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT]
    ) -> str:
        return "\n\n".join(
            (
                *maybe_iter_with_title(title="# Identity", sections=self._make_role_def_prompt()),
                *maybe_iter_with_title(title="# Game Rule", sections=self._make_game_rule_prompt()),
                *maybe_iter_with_title(
                    title="# Current Notes",
                    sections=leaves_to_xmls(items=self._prompt_note(note_state=note_state)),
                ),
            )
        )

    def _make_guess_prompt(
        self, *, game_state: AgentGameStateInterface[IT, GT, FT, RT]
    ) -> Iterator[str]:
        yield from maybe_iter_with_title(
            title="# Game Info",
            sections=leaves_to_xmls(
                items=self.prompt_game_info(trajectory=game_state.trajectory, final_result=None)
            ),
        )

        yield from maybe_iter_with_title(
            title="# Guess History",
            sections=self._make_trajectory_prompt(
                trajectory=game_state.trajectory, final_result=None
            ),
        )

        yield from maybe_iter_with_title(
            title="# Latest Analysis",
            sections=leaves_to_xmls(items=self._prompt_analysis(analysis=game_state.last_analysis)),
        )

        yield "# Instruction"

        if self._do_analyze:
            if len(game_state.turns) == 0:
                yield "Analyze the game carefully, then plan and make your new guess."
            else:
                yield (
                    "Analyze the game carefully with previous analysis and latest feedback, "
                    "then plan and make your new guess."
                )
        else:
            yield "Analyze the game carefully and make your new guess."

        yield from self.make_guess_detail_prompt(game_state=game_state)
        yield "Make your response clear and concise."
        guess_example: BaseModel = self.get_guess_example(game_state=game_state)

        yield make_json_prompt(
            example=AnalyzedGuess(
                analysis=Analysis(analysis="...", plan="..."), guess=guess_example
            )
            if self._do_analyze
            else guess_example
        )

    def _make_game_record_prompt(self, *, game_record: GameRecord[IT, GT, FT, RT]) -> Iterator[str]:
        yield from two_layer_to_xml(
            key="Game Info",
            items=self.prompt_game_info(
                trajectory=game_record.trajectory, final_result=game_record.final_result
            ),
        )

        yield from self._make_trajectory_prompt(
            trajectory=game_record.trajectory, final_result=game_record.final_result
        )

        yield from two_layer_to_xml(
            key="Latest Analysis", items=self._prompt_analysis(analysis=game_record.last_analysis)
        )

        yield from two_layer_to_xml(
            key="Final Result", items=self.prompt_final_result(game_record=game_record)
        )

    def _make_reflection_format_prompt(self) -> Iterator[str]:
        yield from self.make_reflect_detail_prompt()
        yield "Make your response clear and concise."
        yield make_json_prompt(example=Reflection(summary="...", reflection="..."))

    def _make_history_prompt(
        self, *, note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT]
    ) -> Iterator[str]:
        for index, summary in enumerate(note_state.history):
            yield from maybe_to_xml(
                key=f"Trial {index + 1}",
                values=(
                    *self._make_game_record_prompt(game_record=summary.game_record),
                    *two_layer_to_xml(
                        key="Reflection",
                        items=self._prompt_reflection(reflection=summary.reflection),
                    ),
                ),
            )

    def _make_role_def_prompt(self) -> Iterator[str]:
        yield self.ROLE_DEFINITION

    def _make_game_rule_prompt(self) -> Iterator[str]:
        yield self.GAME_RULE

    def _make_trajectory_prompt(
        self, *, trajectory: Trajectory[IT, GT, FT], final_result: RT | None
    ) -> Iterator[str]:
        for index, turn in enumerate(trajectory.turns):
            yield from maybe_to_xml(
                key=f"Guess {index + 1}",
                values=leaves_to_xmls(
                    items=chain(
                        self.prompt_guess(
                            trajectory=trajectory,
                            turn_id=index,
                            guess=turn.guess,
                            final_result=final_result,
                        ),
                        self.prompt_feedback(
                            trajectory=trajectory,
                            turn_id=index,
                            guess=turn.guess,
                            feedback=turn.feedback,
                            final_result=final_result,
                        ),
                    ),
                ),
            )

    def _prompt_note(
        self, *, note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT]
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_model(data=note_state.note)

    def _prompt_analysis(self, *, analysis: Analysis | None) -> Iterator[tuple[str, str]]:
        if analysis is not None:
            yield from self._prompt_model(data=analysis)

    def _prompt_reflection(self, *, reflection: Reflection) -> Iterator[tuple[str, str]]:
        yield from self._prompt_model(data=reflection)

    def _prompt_model(self, *, data: BaseModel) -> Iterator[tuple[str, str]]:
        for key, field in type(data).model_fields.items():
            yield str(field.title), str(getattr(data, key))

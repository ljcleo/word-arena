from collections.abc import Iterable, Iterator
from itertools import chain
from typing import override

from pydantic import BaseModel, create_model

from ...common.game.common import Trajectory
from ...common.llm.common import Message
from ...common.llm.llm import LLM
from ...common.player.common import AnalyzedGuess, GameRecord
from ...common.player.engine.base import BasePlayerEngine
from ...common.player.state import PlayerGameStateInterface, PlayerNoteStateInterface
from .common import Analysis, Note, Reflection
from .prompter.base import BaseAgentPrompter, BaseAgentPrompterPromptConfig


class NoteHintPromptConfig(BaseModel):
    law: str
    strategy: str


class AnalysisHintPromptConfig(BaseModel):
    analysis: str
    plan: str


class ReflectionHintPromptConfig(BaseModel):
    summary: str
    reflection: str


class AgentHintPromptConfig(BaseModel):
    note: NoteHintPromptConfig
    analysis: AnalysisHintPromptConfig
    reflection: ReflectionHintPromptConfig


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


class AgentPlayerEngine[IT, GT: BaseModel, FT, RT](
    BasePlayerEngine[Note, IT, Analysis, GT, FT, RT, Reflection]
):
    def __init__(
        self,
        *,
        model: LLM,
        do_analyze: bool,
        prompter: BaseAgentPrompter[BaseAgentPrompterPromptConfig, IT, GT, FT, RT],
        prompt_config: AgentHintPromptConfig,
    ):
        self._model: LLM = model
        self._do_analyze: bool = do_analyze
        self._prompter: BaseAgentPrompter[BaseAgentPrompterPromptConfig, IT, GT, FT, RT] = prompter
        self._prompt_config: AgentHintPromptConfig = prompt_config

    @override
    def create_note(self) -> Note:
        return self._model.query(
            Message.human(
                "# Instruction",
                "Initialize some notes that help you make a good guess in a turn.",
                *self._make_note_format_prompt(),
            ),
            format=Note,
            system_instruction=self._make_reflect_system_instruction(
                status="You have not played the game yet."
            ),
        )

    @override
    def analyze_and_guess(
        self,
        *,
        note_state: PlayerNoteStateInterface[Note, IT, Analysis, GT, FT, RT, Reflection],
        game_state: PlayerGameStateInterface[IT, Analysis, GT, FT, RT],
    ) -> AnalyzedGuess[Analysis, GT]:
        system_instruction: str = self._make_guess_system_instruction(note_state=note_state)

        messages: list[Message] = [
            Message.human(*self._make_guess_prompt(game_state=game_state)),
        ]

        analysis: Analysis | None = None
        guess: GT

        if self._do_analyze:
            full_guess: BaseModel = self._model.query(
                *messages,
                format=create_model("Guess", analysis=Analysis, guess=self._prompter.GUESS_CLS),
                system_instruction=system_instruction,
            )

            analysis = getattr(full_guess, "analysis")
            guess = getattr(full_guess, "guess")
            assert analysis is not None
        else:
            guess = self._model.query(
                *messages, format=self._prompter.GUESS_CLS, system_instruction=system_instruction
            )

        return AnalyzedGuess(analysis=analysis, guess=guess)

    @override
    def summarize_and_reflect(
        self,
        *,
        note_state: PlayerNoteStateInterface[Note, IT, Analysis, GT, FT, RT, Reflection],
        game_state: PlayerGameStateInterface[IT, Analysis, GT, FT, RT],
    ) -> Reflection:
        return self._model.query(
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

    @override
    def update_note(
        self, *, note_state: PlayerNoteStateInterface[Note, IT, Analysis, GT, FT, RT, Reflection]
    ) -> Note:
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
            format=Note,
            system_instruction=self._make_reflect_system_instruction(
                status="You have played the game a few times."
            ),
        )

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
        yield self._prompter.prompt_config.note_detail
        yield "Make your response clear and concise."
        yield make_json_prompt(example=Note(law="...", strategy="..."))

    def _make_guess_system_instruction(
        self, *, note_state: PlayerNoteStateInterface[Note, IT, Analysis, GT, FT, RT, Reflection]
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
        self, *, game_state: PlayerGameStateInterface[IT, Analysis, GT, FT, RT]
    ) -> Iterator[str]:
        yield from maybe_iter_with_title(
            title="# Game Info",
            sections=leaves_to_xmls(
                items=self._prompter.prompt_game_info(
                    trajectory=game_state.trajectory, final_result=None
                )
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

        yield self._prompter.get_guess_detail(trajectory=game_state.trajectory)
        yield "Make your response clear and concise."

        guess_example: GT = self._prompter.get_guess_example(trajectory=game_state.trajectory)

        yield make_json_prompt(
            example=AnalyzedGuess(
                analysis=Analysis(analysis="...", plan="..."), guess=guess_example
            )
            if self._do_analyze
            else guess_example
        )

    def _make_game_record_prompt(
        self, *, game_record: GameRecord[IT, Analysis, GT, FT, RT]
    ) -> Iterator[str]:
        yield from two_layer_to_xml(
            key="Game Info",
            items=self._prompter.prompt_game_info(
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
            key="Final Result",
            items=self._prompter.prompt_final_result(
                trajectory=game_record.trajectory, final_result=game_record.final_result
            ),
        )

    def _make_reflection_format_prompt(self) -> Iterator[str]:
        yield self._prompter.prompt_config.reflection_detail
        yield "Make your response clear and concise."
        yield make_json_prompt(example=Reflection(summary="...", reflection="..."))

    def _make_history_prompt(
        self, *, note_state: PlayerNoteStateInterface[Note, IT, Analysis, GT, FT, RT, Reflection]
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
        yield self._prompter.prompt_config.role_definition

    def _make_game_rule_prompt(self) -> Iterator[str]:
        yield self._prompter.prompt_config.game_rule

    def _make_trajectory_prompt(
        self, *, trajectory: Trajectory[IT, GT, FT], final_result: RT | None
    ) -> Iterator[str]:
        for index, turn in enumerate(trajectory.turns):
            yield from maybe_to_xml(
                key=f"Guess {index + 1}",
                values=leaves_to_xmls(
                    items=chain(
                        self._prompter.prompt_guess(
                            trajectory=trajectory,
                            turn_id=index,
                            guess=turn.guess,
                            final_result=final_result,
                        ),
                        self._prompter.prompt_feedback(
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
        self, *, note_state: PlayerNoteStateInterface[Note, IT, Analysis, GT, FT, RT, Reflection]
    ) -> Iterator[tuple[str, str]]:
        note: Note = note_state.note
        prompt: NoteHintPromptConfig = self._prompt_config.note
        yield prompt.law, note.law
        yield prompt.strategy, note.strategy

    def _prompt_analysis(self, *, analysis: Analysis | None) -> Iterator[tuple[str, str]]:
        if analysis is not None:
            prompt: AnalysisHintPromptConfig = self._prompt_config.analysis
            yield prompt.analysis, analysis.analysis
            yield prompt.plan, analysis.plan

    def _prompt_reflection(self, *, reflection: Reflection) -> Iterator[tuple[str, str]]:
        prompt: ReflectionHintPromptConfig = self._prompt_config.reflection
        yield prompt.summary, reflection.summary
        yield prompt.reflection, reflection.reflection

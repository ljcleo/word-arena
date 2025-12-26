from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator

from ..game.common import GameRecord, Turn
from ..memory.common import Analysis, GameSummary, Reflection
from .base import BaseFinalResultFormatter, BaseInGameFormatter


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


class BaseAgentCommonFormatter[IT, HT, GT, FT, NT](BaseInGameFormatter[IT, HT, GT, FT], ABC):
    @classmethod
    def format_note_xml(cls, *, note: NT) -> Iterator[str]:
        yield from leaves_to_xmls(items=cls.format_note(note=note))

    @classmethod
    def format_analysis(cls, *, analysis: Analysis) -> Iterator[tuple[str, str]]:
        yield "Analysis", analysis.analysis
        yield "Plan", analysis.plan

    @classmethod
    @abstractmethod
    def format_note(cls, *, note: NT) -> Iterator[tuple[str, str]]:
        raise NotImplementedError()


class BaseAgentPlayerFormatter[IT, HT, GT, FT, NT](
    BaseAgentCommonFormatter[IT, HT, GT, FT, NT], ABC
):
    @classmethod
    def format_game_info_xml(cls, *, game_info: IT) -> Iterator[str]:
        yield from leaves_to_xmls(items=cls.format_game_info(game_info=game_info))

    @classmethod
    def format_trajectory(
        cls, *, game_info: IT, trajectory: Iterable[Turn[HT, GT, FT]]
    ) -> Iterator[str]:
        for index, turn in enumerate(trajectory):
            yield from maybe_to_xml(
                key=f"Guess {index + 1}",
                values=cls._format_turn(game_info=game_info, turn=turn),
            )

    @classmethod
    def format_analysis_xml(cls, *, analysis: Analysis) -> Iterator[str]:
        yield from leaves_to_xmls(items=cls.format_analysis(analysis=analysis))

    @classmethod
    def format_hint_xml(cls, *, game_info: IT, hint: HT) -> Iterator[str]:
        yield from leaves_to_xmls(items=cls.format_hint(game_info=game_info, hint=hint))

    @classmethod
    def _format_turn(cls, *, game_info: IT, turn: Turn[HT, GT, FT]) -> Iterator[str]:
        yield from two_layer_to_xml(
            key="Turn Info", items=cls.format_hint(game_info=game_info, hint=turn.hint)
        )

        yield from two_layer_to_xml(
            key="Guess",
            items=cls.format_guess(game_info=game_info, hint=turn.hint, guess=turn.guess),
        )

        yield from two_layer_to_xml(
            key="Feedback",
            items=cls.format_feedback(
                game_info=game_info, hint=turn.hint, guess=turn.guess, feedback=turn.feedback
            ),
        )


class BaseAgentMemoryFormatter[IT, HT, GT, FT, RT, NT](
    BaseAgentCommonFormatter[IT, HT, GT, FT, NT], BaseFinalResultFormatter[RT], ABC
):
    @classmethod
    def format_hint_with_final_result(
        cls, *, game_info: IT, hint: HT, final_result: RT
    ) -> Iterator[tuple[str, str]]:
        yield from cls.format_hint(game_info=game_info, hint=hint)

    @classmethod
    def format_guess_with_final_result(
        cls, *, game_info: IT, hint: HT, guess: GT, final_result: RT
    ) -> Iterator[tuple[str, str]]:
        yield from cls.format_guess(game_info=game_info, hint=hint, guess=guess)

    @classmethod
    def format_feedback_with_final_result(
        cls, *, game_info: IT, hint: HT, guess: GT, feedback: FT, final_result: RT
    ) -> Iterator[tuple[str, str]]:
        yield from cls.format_feedback(
            game_info=game_info, hint=hint, guess=guess, feedback=feedback
        )

    @classmethod
    def format_record(
        cls, *, game_record: GameRecord[IT, HT, GT, FT, RT], latest_analysis: Analysis | None
    ) -> Iterator[str]:
        yield from two_layer_to_xml(
            key="Game Info", items=cls.format_game_info(game_info=game_record.game_info)
        )

        for index, turn in enumerate(game_record.trajectory):
            yield from maybe_to_xml(
                key=f"Guess {index + 1}",
                values=cls._format_turn(
                    game_info=game_record.game_info,
                    turn=turn,
                    final_result=game_record.final_result,
                ),
            )

        if latest_analysis is not None:
            yield from two_layer_to_xml(
                key="Latest Analysis", items=cls.format_analysis(analysis=latest_analysis)
            )

        yield from two_layer_to_xml(
            key="Final Result", items=cls.format_final_result(final_result=game_record.final_result)
        )

    @classmethod
    def format_reflection(cls, *, reflection: Reflection) -> Iterator[tuple[str, str]]:
        yield "Game Summary", reflection.summary
        yield "Reflection", reflection.reflection

    @classmethod
    def format_history(cls, *, history: Iterable[GameSummary[IT, HT, GT, FT, RT]]) -> Iterator[str]:
        for index, summary in enumerate(history):
            yield from maybe_to_xml(
                key=f"Trial {index + 1}",
                values=(
                    *cls.format_record(
                        game_record=summary.game_record, latest_analysis=summary.latest_analysis
                    ),
                    *two_layer_to_xml(
                        key="Reflection", items=cls.format_reflection(reflection=summary.reflection)
                    ),
                ),
            )

    @classmethod
    def _format_turn(
        cls, *, game_info: IT, turn: Turn[HT, GT, FT], final_result: RT
    ) -> Iterator[str]:
        yield from two_layer_to_xml(
            key="Turn Info",
            items=cls.format_hint_with_final_result(
                game_info=game_info, hint=turn.hint, final_result=final_result
            ),
        )

        yield from two_layer_to_xml(
            key="Guess",
            items=cls.format_guess_with_final_result(
                game_info=game_info, hint=turn.hint, guess=turn.guess, final_result=final_result
            ),
        )

        yield from two_layer_to_xml(
            key="Feedback",
            items=cls.format_feedback_with_final_result(
                game_info=game_info,
                hint=turn.hint,
                guess=turn.guess,
                feedback=turn.feedback,
                final_result=final_result,
            ),
        )

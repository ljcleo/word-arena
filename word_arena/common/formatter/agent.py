from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator

from ..game.common import GameRecord, Turn
from ..memory.common import Analysis, GameSummary, Reflection
from .base import BaseFinalResultFormatter, BaseInGameFormatter


class BaseAgentCommonFormatter[IT, HT, GT, FT, ET](BaseInGameFormatter[IT, HT, GT, FT], ABC):
    @classmethod
    def format_analysis(cls, *, analysis: Analysis, is_current: bool) -> Iterator[str]:
        yield f"{'' if is_current else 'Latest '}Analysis:"
        yield "\n".join((f"Analysis: {analysis.analysis}", f"Plan: {analysis.plan}"))

    @classmethod
    def format_turn(cls, *, game_info: IT, turn: Turn[HT, GT, FT]) -> Iterator[str]:
        yield from cls.format_hint(game_info=game_info, hint=turn.hint)
        yield from cls.format_guess(game_info=game_info, hint=turn.hint, guess=turn.guess)

        yield from cls.format_feedback(
            game_info=game_info, hint=turn.hint, guess=turn.guess, feedback=turn.feedback
        )

    @classmethod
    def format_record_detail(
        cls,
        *,
        game_info: IT,
        trajectory: Iterable[Turn[HT, GT, FT]],
        latest_analysis: Analysis | None,
        turn_formatter: Callable[[IT, Turn[HT, GT, FT]], Iterator[str]],
    ) -> Iterator[str]:
        yield from cls.format_game_info(game_info=game_info)

        sections: list[str] = []
        for index, turn in enumerate(trajectory):
            sections.extend((f"Guess {index + 1}", *turn_formatter(game_info, turn)))

        if len(sections) > 0:
            yield "Guess History:"
            yield "\n".join(sections)

        if latest_analysis is not None:
            yield from cls.format_analysis(analysis=latest_analysis, is_current=False)

    @classmethod
    @abstractmethod
    def format_experience(cls, *, experience: ET) -> Iterator[str]:
        raise NotImplementedError()


class BaseAgentPlayerFormatter[IT, HT, GT, FT, ET](
    BaseAgentCommonFormatter[IT, HT, GT, FT, ET], ABC
):
    @classmethod
    def format_in_game_record(
        cls,
        *,
        game_info: IT,
        trajectory: Iterable[Turn[HT, GT, FT]],
        latest_analysis: Analysis | None,
    ) -> Iterator[str]:
        yield from cls.format_record_detail(
            game_info=game_info,
            trajectory=trajectory,
            latest_analysis=latest_analysis,
            turn_formatter=lambda i, t: cls.format_turn(game_info=i, turn=t),
        )


class BaseAgentMemoryFormatter[IT, HT, GT, FT, RT, ET](
    BaseAgentCommonFormatter[IT, HT, GT, FT, ET], BaseFinalResultFormatter[RT], ABC
):
    @classmethod
    def format_hint_with_final_result(
        cls, *, game_info: IT, hint: HT, final_result: RT
    ) -> Iterator[str]:
        yield from cls.format_hint(game_info=game_info, hint=hint)

    @classmethod
    def format_guess_with_final_result(
        cls, *, game_info: IT, hint: HT, guess: GT, final_result: RT
    ) -> Iterator[str]:
        yield from cls.format_guess(game_info=game_info, hint=hint, guess=guess)

    @classmethod
    def format_feedback_with_final_result(
        cls, *, game_info: IT, hint: HT, guess: GT, feedback: FT, final_result: RT
    ) -> Iterator[str]:
        yield from cls.format_feedback(
            game_info=game_info, hint=hint, guess=guess, feedback=feedback
        )

    @classmethod
    def format_turn_with_final_result(
        cls, *, game_info: IT, turn: Turn[HT, GT, FT], final_result: RT
    ) -> Iterator[str]:
        yield from cls.format_hint_with_final_result(
            game_info=game_info, hint=turn.hint, final_result=final_result
        )

        yield from cls.format_guess_with_final_result(
            game_info=game_info, hint=turn.hint, guess=turn.guess, final_result=final_result
        )

        yield from cls.format_feedback_with_final_result(
            game_info=game_info,
            hint=turn.hint,
            guess=turn.guess,
            feedback=turn.feedback,
            final_result=final_result,
        )

    @classmethod
    def format_record(
        cls, *, game_record: GameRecord[IT, HT, GT, FT, RT], latest_analysis: Analysis | None
    ) -> Iterator[str]:
        yield from cls.format_record_detail(
            game_info=game_record.game_info,
            trajectory=game_record.trajectory,
            latest_analysis=latest_analysis,
            turn_formatter=lambda i, t: cls.format_turn_with_final_result(
                game_info=i, turn=t, final_result=game_record.final_result
            ),
        )

        yield from cls.format_final_result(final_result=game_record.final_result)

    @classmethod
    def format_reflection(cls, *, reflection: Reflection) -> Iterator[str]:
        yield "Reflection:"
        yield f"Game Summary: {reflection.summary}\nReflection: {reflection.reflection}"

    @classmethod
    def format_history(cls, *, history: Iterable[GameSummary[IT, HT, GT, FT, RT]]) -> Iterator[str]:
        for index, summary in enumerate(history):
            yield "\n".join(
                (
                    f"Trial {index + 1}",
                    *cls.format_record(
                        game_record=summary.game_record, latest_analysis=summary.latest_analysis
                    ),
                    *cls.format_reflection(reflection=summary.reflection),
                )
            )

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator

from ..memory.common import Analysis, GameRecord, GameSummary, Reflection, Turn
from .base import BaseFinalResultFormatter, BaseInGameFormatter


class BaseAgentFormatter[IT, HT, GT, FT, RT, ET](ABC):
    @staticmethod
    def format_analysis(*, analysis: Analysis) -> Iterator[str]:
        yield "Analysis from the Last Guess:"

        yield "\n".join(
            (
                f"Past analysis summary: {analysis.past_analysis_summary}",
                f"Analysis update: {analysis.current_analysis}",
                f"Plan: {analysis.plan}",
            )
        )

    @classmethod
    def format_trajectory(
        cls, *, game_info: IT, trajectory: Iterable[Turn[HT, GT, FT]], final_result: RT | None
    ) -> Iterator[str]:
        yield "Guess History:"
        sections: list[str] = []

        for index, turn in enumerate(trajectory):
            sections.extend(
                (
                    f"Guess {index + 1}",
                    *cls.format_turn(game_info=game_info, turn=turn, final_result=final_result),
                )
            )

        if len(sections) == 0:
            sections.append("(Empty)")

        yield "\n".join(sections)

    @classmethod
    def format_in_game_record(
        cls,
        *,
        game_info: IT,
        trajectory: Iterable[Turn[HT, GT, FT]],
        latest_analysis: Analysis | None,
    ) -> Iterator[str]:
        yield from cls.get_in_game_formatter_cls().format_game_info(game_info=game_info)

        yield from cls.format_trajectory(
            game_info=game_info, trajectory=trajectory, final_result=None
        )

        if latest_analysis is not None:
            yield from cls.format_analysis(analysis=latest_analysis)

    @classmethod
    def format_record(cls, *, record: GameRecord[IT, HT, GT, FT, RT]) -> Iterator[str]:
        yield from cls.format_in_game_record(
            game_info=record.game_info,
            trajectory=record.trajectory,
            latest_analysis=record.latest_analysis,
        )

        yield from cls.get_final_result_formatter_cls().format_final_result(
            final_result=record.final_result
        )

    @staticmethod
    def format_reflection(*, reflection: Reflection) -> Iterator[str]:
        yield "Reflection:"
        yield f"Summary: {reflection.summary}\nLessons: {reflection.lessons}"

    @classmethod
    def format_history(
        cls,
        *,
        history: Iterable[GameSummary[IT, HT, GT, FT, RT]],
    ) -> Iterator[str]:
        for index, summary in enumerate(history):
            yield "\n".join(
                (
                    f"Trial {index + 1}",
                    *cls.format_record(record=summary.record),
                    *cls.format_reflection(reflection=summary.reflection),
                )
            )

    @staticmethod
    @abstractmethod
    def format_turn(
        *, game_info: IT, turn: Turn[HT, GT, FT], final_result: RT | None
    ) -> Iterator[str]:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def format_experience(*, experience: ET) -> Iterator[str]:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_in_game_formatter_cls() -> type[BaseInGameFormatter[IT, HT, GT, FT]]:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_final_result_formatter_cls() -> type[BaseFinalResultFormatter[RT]]:
        raise NotImplementedError()

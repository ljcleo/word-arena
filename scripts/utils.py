from json import dumps

from common import GAME_CONFIG_PATH, LLM_CONFIG_PATH
from pydantic import BaseModel


def input_game_key() -> str:
    games: list[str] = sorted(p.stem for p in GAME_CONFIG_PATH.iterdir())
    for index, game in enumerate(games):
        print(f"{index}. {game}")

    return games[int(input("Game Index: "))]


def input_llm_key() -> str:
    llms: list[str] = sorted(p.stem for p in LLM_CONFIG_PATH.iterdir())
    for index, llm in enumerate(llms):
        print(f"{index}. {llm}")

    return llms[int(input("LLM Index: "))]


def make_cls_prefix(*, key: str) -> str:
    return "".join(part.capitalize() for part in key.split("_"))


def try_validate[T: BaseModel, U](*, cls: type[T] | None, data: U) -> T | U:
    return data if cls is None else cls.model_validate_json(dumps(data), strict=True)

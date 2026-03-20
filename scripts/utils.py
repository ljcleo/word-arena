from pathlib import Path

from build_gym import GYM_BUILDERS


def input_game_key() -> str:
    games: list[str] = list(GYM_BUILDERS.keys())
    for index, game in enumerate(games):
        print(f"{index}. {game}")

    return games[int(input("Game Index: "))]


def input_llm_key() -> str:
    llms: list[str] = sorted(p.stem for p in Path("./config/llm").glob("*.json"))
    for index, llm in enumerate(llms):
        print(f"{index}. {llm}")

    return llms[int(input("LLM Index: "))]

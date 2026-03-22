from build_gym import GAME_CONFIG_PATH
from build_llm import LLM_CONFIG_PATH


def input_game_key() -> str:
    games: list[str] = sorted(p.stem for p in GAME_CONFIG_PATH.glob("*.json"))
    for index, game in enumerate(games):
        print(f"{index}. {game}")

    return games[int(input("Game Index: "))]


def input_llm_key() -> str:
    llms: list[str] = sorted(p.stem for p in LLM_CONFIG_PATH.glob("*.json"))
    for index, llm in enumerate(llms):
        print(f"{index}. {llm}")

    return llms[int(input("LLM Index: "))]

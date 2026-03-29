from pathlib import Path

GAME_CONFIG_PATH: Path = Path("./config/games")
LLM_CONFIG_PATH: Path = Path("./config/llms")
PLAYER_CONFIG_PATH: Path = Path("./config/players")


def log(key: str, value: str) -> None:
    print(f"{key}: {value}")

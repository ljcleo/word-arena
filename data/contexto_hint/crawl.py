from logging import WARNING, getLogger
from pathlib import Path

import httpx
from tenacity import before_sleep_log, retry, wait_random


@retry(wait=wait_random(max=1), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
def get_top(game_id: int, /, *, proxy: str | None = None) -> list[str] | None:
    response: httpx.Response = httpx.get(
        f"https://api.contexto.me/machado/en/top/{game_id}", proxy=proxy
    )

    if response.status_code == 200:
        return response.json()["words"]
    elif response.status_code == 500:
        return None
    else:
        raise RuntimeError(response.status_code, response.reason_phrase, response.text)


if __name__ == "__main__":
    target_dir = Path("./games")
    target_dir.mkdir(exist_ok=True)

    for game_id in range(2000):
        target_file: Path = target_dir / f"{game_id}.txt"

        if not target_file.exists():
            top_words: list[str] | None = get_top(game_id)

            if top_words is None:
                print("Break", game_id)
                break

            target_file.write_text("\n".join(top_words))
            print("Crawl", game_id)

    print("Done")

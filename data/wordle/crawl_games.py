import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import httpx
from tenacity import before_sleep_log, retry, wait_random


@retry(
    wait=wait_random(max=3),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING),
)
def get_word(*, target_date: date) -> str:
    date_str: str = target_date.strftime("%Y-%m-%d")
    response: httpx.Response = httpx.get(f"https://www.nytimes.com/svc/wordle/v2/{date_str}.json")

    if response.status_code == 200:
        return response.json()["solution"]
    else:
        raise RuntimeError(response.status_code, response.reason_phrase, response.text)


def main() -> None:
    target_file: Path = Path("./games.txt")

    target_date: date = (
        date(2021, 6, 19)
        if len(sys.argv) == 1
        else datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    )

    while target_date <= date.today():
        print(target_date.strftime("%Y-%m-%d"))
        with target_file.open("a", encoding="utf8") as f:
            print(get_word(target_date=target_date), file=f)

        target_date += timedelta(days=1)


if __name__ == "__main__":
    main()

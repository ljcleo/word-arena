from collections.abc import Iterator
from datetime import date, timedelta
from json import loads
from logging import WARNING, getLogger
from pathlib import Path
from sqlite3 import Connection, Cursor, connect
from typing import Any
from warnings import warn

from pyvirtualdisplay.display import Display
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from tenacity import before_sleep_log, retry, wait_random


def parse_text(text: str) -> Iterator[Any]:
    while text != "":
        header, _, text = text.partition("\n")
        len_doc = int(header)
        yield loads(text[:len_doc])
        text = text[len_doc:]


def parse_doc(doc: dict[str, Any]) -> str:
    return doc["documentChange"]["document"]["fields"]["answer"]["stringValue"]


@retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
def get_word(date_str: str) -> str | None:
    log_file: Path = Path("./log.txt")
    log_file.open("w").close()

    try:
        display: Display = Display()
        display.start()

        options: Options = Options()
        options.add_argument("--proxy-server=http://127.0.0.1:9090")
        options.add_argument("--disable-application-cache")
        options.add_argument("--ignore-certificate-errors")
        service: Service = Service(executable_path="/snap/bin/chromium.chromedriver")
        driver: Chrome = Chrome(service=service, options=options)

        try:
            driver.implicitly_wait(120)
            driver.get(f"https://letroso.com/en/previous/{date_str}")
            driver.find_element(By.CLASS_NAME, "cursor")
        except Exception as e:
            warn(f"error in crawling, will try to extract existing data: {repr(e)}")
            raise
        finally:
            driver.quit()
            display.stop()

        with log_file.open(encoding="utf8") as f:
            for row in f:
                doc: dict[str, Any] = loads(row)

                if doc["status_code"] == 200:
                    for candidate in parse_text(doc["text"]):
                        for _, data in candidate:
                            for chunk in data:
                                if isinstance(chunk, dict) and "documentChange" in chunk:
                                    return parse_doc(chunk)
    except Exception as e:
        warn(f"system error: {repr(e)}")
        raise
    finally:
        log_file.unlink(missing_ok=True)

    return None


def main() -> None:
    con: Connection = connect("./games.db")
    cur: Cursor = con.cursor()

    try:
        with con:
            is_table_exist: bool = bool(
                cur.execute("SELECT 1 FROM sqlite_master WHERE name = 'game'").fetchone()
            )

        if not is_table_exist:
            with con:
                cur.execute("CREATE TABLE game(game_id, word_id)")

        target_date: date = date(2024, 9, 1)
        game_id: int = 0

        while target_date <= date.today():
            with con:
                has_game: bool = bool(
                    cur.execute("SELECT 1 FROM game WHERE game_id = ?", (game_id,)).fetchone()
                )

            if has_game:
                target_date += timedelta(days=1)
                game_id += 1
                continue

            date_str: str = target_date.strftime("%Y-%m-%d")
            print(date_str)

            try:
                word: str | None = get_word(date_str=date_str)
            except Exception as e:
                warn(f"{date_str}: {repr(e)}")
                target_date += timedelta(days=1)
                game_id += 1
                continue

            if word is None:
                warn(f"{date_str}: no valid data")
                target_date += timedelta(days=1)
                game_id += 1
                continue

            with con:
                word_info: tuple[int] | None = cur.execute(
                    "SELECT word_id FROM word WHERE word = ?", (word,)
                ).fetchone()

            if word_info is None:
                warn(f"{date_str}: word {word} not in word database")
                target_date += timedelta(days=1)
                game_id += 1
                continue

            with con:
                cur.execute("INSERT INTO game VALUES(?, ?)", (game_id, word_info[0]))

            target_date += timedelta(days=1)
            game_id += 1
    finally:
        con.close()


if __name__ == "__main__":
    main()

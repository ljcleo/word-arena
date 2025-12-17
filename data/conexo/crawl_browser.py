import json
import warnings
from collections.abc import Iterator
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from pyvirtualdisplay.display import Display
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def parse_text(text: str) -> Iterator[Any]:
    while text != "":
        header, _, text = text.partition("\n")
        len_doc = int(header)
        yield json.loads(text[:len_doc])
        text = text[len_doc:]


def parse_doc(doc: dict[str, Any]) -> dict[str, int | list[str] | list[dict[str, list[int] | str]]]:
    fields: dict[str, Any] = doc["documentChange"]["document"]["fields"]
    game_id: int = int(fields["id"]["integerValue"])

    words: list[str] = [
        value["stringValue"] for value in fields["startingBoard"]["arrayValue"]["values"]
    ]

    groups: list[dict[str, list[int] | str]] = [
        {
            "indices": [
                words.index(value["stringValue"])
                for value in group_value["mapValue"]["fields"]["words"]["arrayValue"]["values"]
            ],
            "theme": group_value["mapValue"]["fields"]["theme"]["stringValue"],
        }
        for group_value in fields["groups"]["arrayValue"]["values"]
    ]

    return {"id": game_id, "words": words, "groups": groups}


def crawl(target_date: date, out_dir: Path):
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
            driver.get(f"https://conexo.ws/en/previous/{target_date.strftime('%Y-%m-%d')}")
            driver.find_element(By.CLASS_NAME, "board-item")
        except Exception as e:
            warnings.warn(f"error in crawling, will try to extract existing data: {repr(e)}")
        finally:
            driver.quit()
            display.stop()

        buffer: list[dict[str, int | list[str] | list[dict[str, list[int] | str]]]] = []

        with log_file.open(encoding="utf8") as f:
            for row in f:
                doc: dict[str, Any] = json.loads(row)

                if doc["status_code"] == 200:
                    for candidate in parse_text(doc["text"]):
                        for _, data in candidate:
                            for chunk in data:
                                if isinstance(chunk, dict) and "documentChange" in chunk:
                                    buffer.append(parse_doc(chunk))
                                    break

        for doc in buffer:
            with (out_dir / f"{doc['id']}.json").open("w", encoding="utf8") as f:
                json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
                break
    except Exception as e:
        warnings.warn(f"system error: {repr(e)}")
    finally:
        log_file.unlink(missing_ok=True)


def main():
    out_dir: Path = Path("./games")
    out_dir.mkdir(exist_ok=True)
    target_date: date = date(2024, 2, 1)
    expected_id: int = 0

    while target_date <= date.today():
        if not (out_dir / f"{expected_id}.json").exists():
            print(target_date.strftime("%Y-%m-%d"), expected_id)
            crawl(target_date, out_dir)

        target_date += timedelta(days=1)
        expected_id += 1


if __name__ == "__main__":
    main()

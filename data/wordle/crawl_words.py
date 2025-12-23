import httpx


def main() -> None:
    response: httpx.Response = httpx.get(
        "https://www.nytimes.com/games-assets/v2/7471.ca837e2d94ae3f5e505b.js"
    )

    if response.status_code == 200:
        words: set[str] = eval(f"{{{response.text.partition('const o=[')[2].partition(']')[0]}}}")
        with open("./words.txt", "w", encoding="utf8") as f:
            print(*sorted(words), sep="\n", file=f)
    else:
        raise RuntimeError(response.status_code, response.reason_phrase, response.text)


if __name__ == "__main__":
    main()

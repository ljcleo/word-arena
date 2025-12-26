from collections.abc import Iterable, Iterator

from pydantic import BaseModel


def make_json_prompt(*, example: BaseModel) -> str:
    return f"Respond in JSON format like `{example.model_dump_json()}`."


def maybe_iter_with_title(*, title: str, sections: Iterable[str]) -> Iterator[str]:
    flag: bool = False

    for section in sections:
        if not flag:
            yield title
            flag = True

        yield section

from collections.abc import Iterator

from pydantic import BaseModel


def format_model(data: BaseModel, /) -> Iterator[tuple[str, str]]:
    for key, field in type(data).model_fields.items():
        yield str(field.title), str(getattr(data, key))

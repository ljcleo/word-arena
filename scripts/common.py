def log(key: str, value: str) -> None:
    print(f"{key}: {value}")


def make_cls_prefix(*, key: str) -> str:
    return "".join(part.capitalize() for part in key.split("_"))

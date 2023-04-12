def to_snake_case(val: str) -> str:
    return "".join(["_" + i.lower() if i.isupper() else i for i in val]).lstrip("_")

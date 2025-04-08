import math


def secs_to_mmss(value: int) -> str:
    return f"{math.floor(value / 60)}:{int(value % 60)}"


def truncate(text: str, length: int) -> str:
    if len(text) >= length:
        return text[:length - 3] + "..."
    return text
